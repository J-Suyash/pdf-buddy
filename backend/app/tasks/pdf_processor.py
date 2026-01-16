from app.tasks.celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Job, JobStatus, Document, Question
from app.services.llama_service import llama_service
from app.services.datalab_service import datalab_service
from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
import logging
import hashlib
import os
import shutil
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

# Ensure permanent storage directory exists
PERMANENT_STORAGE_DIR = settings.permanent_storage_dir
os.makedirs(PERMANENT_STORAGE_DIR, exist_ok=True)


@celery_app.task(bind=True, max_retries=3, name="process_pdf_task")
def process_pdf_task(self, job_id: str, file_paths: list):
    """
    Process PDF files using Datalab browser automation (primary) with LlamaCloud API fallback.

    Processing flow:
    1. Update job status to processing
    2. Try Datalab browser automation first (primary method)
    3. If Datalab fails, fall back to LlamaCloud API
    4. Parse and extract questions
    5. Store questions in database
    6. Generate embeddings
    7. Index in Qdrant
    8. Update job status to completed

    Datalab is preferred because:
    - Uses browser automation for better anti-bot detection
    - No API rate limits
    - More reliable for complex PDFs
    - Free to use
    """
    import asyncio

    # Create a new engine for this task to avoid event loop issues with asyncpg
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        # Use NullPool to avoid keeping connections open in Celery workers
        # poolclass=NullPool
    )

    # Create a local session factory
    task_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def _run_task():
        try:
            await _process_pdf_async(job_id, file_paths, task_session_maker)
        finally:
            await engine.dispose()

    try:
        # Run async function
        asyncio.run(_run_task())
        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"PDF processing failed for job {job_id}: {exc}")

        # Update job with error using a fresh engine/loop context
        # We need to recreate the engine/session for the error handler if the main block failed
        # But simpler is to run it in a new loop if needed, or re-use logic
        # For simplicity, we'll try to run the error handler in a fresh run
        async def _run_error_handler():
            err_engine = create_async_engine(settings.database_url)
            err_session = sessionmaker(
                err_engine, class_=AsyncSession, expire_on_commit=False
            )
            try:
                await _mark_job_failed(job_id, str(exc), err_session)
            finally:
                await err_engine.dispose()

        asyncio.run(_run_error_handler())

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


async def _mark_job_failed(job_id: str, error_message: str, session_maker):
    """Mark job as failed with error message."""
    async with session_maker() as session:
        await session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.FAILED.value, error_message=error_message)
        )
        await session.commit()


async def _process_pdf_async(job_id: str, file_paths: list, session_maker):
    """Async helper for PDF processing with Datalab primary and Llama fallback."""
    async with session_maker() as session:
        try:
            # Update status to processing
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(status=JobStatus.PROCESSING.value, progress=5)
            )
            await session.commit()

            logger.info(f"Started processing {len(file_paths)} files for job {job_id}")

            total_questions = 0
            total_pages = 0
            all_questions_for_indexing = []

            # Process each PDF file
            for idx, file_path in enumerate(file_paths):
                try:
                    logger.info(
                        f"Processing file {idx + 1}/{len(file_paths)}: {file_path}"
                    )

                    # Calculate file hash
                    file_hash = _calculate_file_hash(file_path)
                    filename = os.path.basename(file_path)

                    # Copy to permanent storage
                    permanent_file_path = os.path.join(
                        PERMANENT_STORAGE_DIR, f"{file_hash}_{filename}"
                    )
                    shutil.copy2(file_path, permanent_file_path)
                    logger.info(
                        f"Copied file to permanent storage: {permanent_file_path}"
                    )

                    # Create document record
                    document = Document(
                        job_id=job_id,
                        filename=filename,
                        file_hash=file_hash,
                        file_path=permanent_file_path,  # Store the permanent path
                    )
                    session.add(document)
                    await session.flush()  # Get document ID

                    # Try Datalab browser automation first (primary method)
                    logger.info(f"Attempting Datalab browser automation for {filename}...")
                    try:
                        extraction_result = await datalab_service.process_pdf(
                            file_path=file_path,
                            job_id=job_id,
                        )

                        # Parse Datalab response
                        parsed_result = datalab_service.parse_response(extraction_result, job_id)

                        if not parsed_result.success:
                            raise RuntimeError(f"Datalab processing failed: {parsed_result.status}")

                        # Convert Datalab result to expected format
                        extracted_text = parsed_result.markdown
                        pages = [{"text": parsed_result.markdown, "page_num": 1}]
                        structured_data = {
                            "header": {},  # Datalab doesn't provide structured header
                            "part_a": {"questions": []},
                            "part_b": {"questions": []},
                            "part_c": {"questions": []},
                        }

                        # Try to extract questions from Datalab chunks
                        questions_by_parts = await _extract_questions_from_datalab(
                            parsed_result, document.id
                        )

                        logger.info(f"Datalab processing successful for {filename}")

                    except Exception as datalab_error:
                        logger.warning(
                            f"Datalab browser automation failed for {filename}: {datalab_error}. "
                            f"Falling back to LlamaCloud API..."
                        )

                        # Fallback to LlamaCloud API
                        logger.info(f"Extracting text from {filename} using LlamaCloud API...")
                        extraction_result = await llama_service.extract_from_pdf(file_path)

                        extracted_text = extraction_result.get("text", "")
                        pages = extraction_result.get("pages", [])
                        structured_data = extraction_result.get("structured_data", {})

                    # Extract exam metadata from structured data
                    logger.info(f"Extracting exam metadata from {filename}...")
                    header = (
                        structured_data.get("header", {})
                        if isinstance(structured_data, dict)
                        else {}
                    )

                    # Update document with metadata and page count
                    document.page_count = len(pages)
                    document.course_code = header.get("course_code")
                    document.course_name = header.get("course_name")
                    document.semester = header.get("semester")
                    document.exam_date = header.get("exam_date_month")

                    # Parse duration (e.g., "3 hours" -> 180 minutes)
                    duration_str = header.get("duration", "")
                    if "hour" in duration_str.lower():
                        try:
                            hours = int("".join(filter(str.isdigit, duration_str)))
                            document.duration_minutes = hours * 60
                        except:
                            document.duration_minutes = None

                    document.total_marks = header.get("max_marks")
                    document.exam_type = "End Semester"  # Default, can be inferred
                    total_pages += len(pages)

                    # Update progress
                    progress = 10 + (idx * 30 // len(file_paths))
                    await session.execute(
                        update(Job)
                        .where(Job.id == job_id)
                        .values(progress=progress, processed_pages=total_pages)
                    )
                    await session.commit()

                    # Parse questions from structured data
                    logger.info(f"Parsing questions from {filename}...")
                    questions_by_parts = await llama_service.extract_questions_by_parts(
                        extracted_text, structured_data=structured_data
                    )

                    # Flatten all questions from all parts
                    questions_data = []
                    for part_questions in questions_by_parts.values():
                        questions_data.extend(part_questions)

                    logger.info(f"Found {len(questions_data)} questions in {filename}")

                    # Store questions in database
                    for q_data in questions_data:
                        question = Question(
                            document_id=document.id,
                            content=q_data["content"],
                            # Part information
                            part=q_data.get("part"),
                            part_marks=q_data.get("part_marks"),
                            question_number=q_data.get("question_number"),
                            unit=q_data.get("unit"),
                            # MCQ fields
                            is_mcq=1 if q_data.get("is_mcq") else 0,
                            options=q_data.get("options"),
                            correct_answer=q_data.get("correct_answer"),
                            # Metadata
                            subject=q_data.get("subject"),
                            topic=q_data.get("topic"),
                            difficulty=q_data.get("difficulty"),
                            question_type=q_data.get("question_type"),
                            year=q_data.get("year"),
                            marks=q_data.get("marks"),
                            # Additional flags
                            is_mandatory=1 if q_data.get("is_mandatory", True) else 0,
                            has_or_option=1
                            if q_data.get("has_or_option", False)
                            else 0,
                        )
                        session.add(question)
                        await session.flush()  # Get question ID

                        # Prepare for embedding and indexing
                        all_questions_for_indexing.append(
                            {
                                "id": question.id,
                                "content": question.content,
                                "document_id": document.id,
                                "part": question.part,
                                "subject": question.subject,
                                "topic": question.topic,
                                "difficulty": question.difficulty,
                                "question_type": question.question_type,
                                "year": question.year,
                                "marks": question.marks,
                            }
                        )

                    total_questions += len(questions_data)
                    await session.commit()

                    # Update progress
                    progress = 40 + (idx * 30 // len(file_paths))
                    await session.execute(
                        update(Job)
                        .where(Job.id == job_id)
                        .values(progress=progress, total_questions=total_questions)
                    )
                    await session.commit()

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    # Continue with other files
                    continue

            # Generate embeddings and index in Qdrant
            if all_questions_for_indexing:
                logger.info(
                    f"Generating embeddings for {len(all_questions_for_indexing)} questions..."
                )

                # Update progress
                await session.execute(
                    update(Job).where(Job.id == job_id).values(progress=75)
                )
                await session.commit()

                # Generate embeddings in batch
                texts = [q["content"] for q in all_questions_for_indexing]
                embeddings = await embedding_service.batch_generate(texts)

                # Prepare data for Qdrant
                qdrant_points = []
                for i, (q, embedding) in enumerate(
                    zip(all_questions_for_indexing, embeddings)
                ):
                    qdrant_points.append(
                        {
                            "question_id": q["id"],
                            "vector": embedding,
                            "text": q["content"],
                            "document_id": q["document_id"],
                            "subject": q["subject"],
                            "topic": q["topic"],
                            "difficulty": q["difficulty"],
                            "question_type": q["question_type"],
                            "year": q["year"],
                            "marks": q["marks"],
                        }
                    )

                # Index in Qdrant
                logger.info(f"Indexing {len(qdrant_points)} questions in Qdrant...")
                indexed_count = await qdrant_service.index_questions(qdrant_points)
                logger.info(f"Successfully indexed {indexed_count} questions")

                # Update qdrant_id in database
                for i, q in enumerate(all_questions_for_indexing):
                    await session.execute(
                        update(Question)
                        .where(Question.id == q["id"])
                        .values(qdrant_id=i)
                    )
                await session.commit()

            # Mark job as completed
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(
                    status=JobStatus.COMPLETED.value,
                    progress=100,
                    total_questions=total_questions,
                    processed_pages=total_pages,
                )
            )
            await session.commit()

            logger.info(
                f"Job {job_id} completed successfully. Processed {total_questions} questions from {total_pages} pages"
            )

            # Clean up temporary files
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(status=JobStatus.FAILED.value, error_message=str(e))
            )
            await session.commit()
            raise


async def _extract_questions_from_datalab(parsed_result, document_id: str):
    """
    Extract questions from Datalab parsed result.

    Datalab returns chunks/blocks with text content. We need to parse these
    into question format compatible with the existing schema.

    Returns:
        Dict with keys "A", "B", "C" containing lists of questions
    """
    from app.services.datalab_service import ParsedDatalabResult

    result = {"A": [], "B": [], "C": []}

    if not isinstance(parsed_result, ParsedDatalabResult):
        logger.warning(f"Invalid parsed result type: {type(parsed_result)}")
        return result

    # Process each page's blocks
    for page in parsed_result.pages:
        for block in page.blocks:
            text = block.text.strip()

            if not text or len(text) < 10:
                continue

            # Try to identify question type from text patterns
            # This is a simple heuristic - can be improved with better parsing

            # Check for question number pattern (e.g., "1.", "Q1.", "1)")
            import re
            question_match = re.match(r'^(\d+)[\.\)]\s*(.+)', text, re.DOTALL)

            if question_match:
                q_num = question_match.group(1)
                q_text = question_match.group(2).strip()

                # Determine part based on question number
                try:
                    num = int(q_num)
                    if 1 <= num <= 20:
                        part = "A"  # MCQs
                        marks = 1
                        is_mcq = True
                    elif 21 <= num <= 25:
                        part = "B"  # Descriptive
                        marks = 8
                        is_mcq = False
                    else:
                        part = "C"  # Scenario
                        marks = 15
                        is_mcq = False
                except:
                    part = "C"
                    marks = 15
                    is_mcq = False

                question_data = {
                    "content": q_text,
                    "question_number": q_num,
                    "part": part,
                    "part_marks": marks,
                    "unit": None,  # Can't determine from text alone
                    "is_mcq": is_mcq,
                    "marks": marks,
                    "question_type": "mcq" if is_mcq else "descriptive",
                    "is_mandatory": True,
                    "has_or_option": False,
                }

                result[part].append(question_data)
            else:
                # No question number found, treat as descriptive text
                # This could be instructions or part of a question
                # For now, skip or add to Part C
                if len(text) > 50:  # Likely a question
                    result["C"].append({
                        "content": text,
                        "question_number": "?",
                        "part": "C",
                        "part_marks": 15,
                        "unit": None,
                        "is_mcq": False,
                        "marks": 15,
                        "question_type": "descriptive",
                        "is_mandatory": False,
                        "has_or_option": False,
                    })

    total = sum(len(q) for q in result.values())
    logger.info(f"Extracted {total} questions from Datalab chunks: A={len(result['A'])}, B={len(result['B'])}, C={len(result['C'])}")

    return result


def _calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
