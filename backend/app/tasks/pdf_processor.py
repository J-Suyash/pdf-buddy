from app.tasks.celery_app import celery_app
from app.core.database import async_session
from app.models import Job, JobStatus, Document, Question
from app.services.llama_service import llama_service
from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
import logging
import hashlib
import os
from sqlalchemy import select, update

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, name="process_pdf_task")
def process_pdf_task(self, job_id: str, file_paths: list):
    """
    Process PDF files:
    1. Update job status to processing
    2. Extract text from PDF using LlamaCloud
    3. Parse and extract questions
    4. Store questions in database
    5. Generate embeddings
    6. Index in Qdrant
    7. Update job status to completed
    """
    import asyncio

    try:
        # Run async function
        asyncio.run(_process_pdf_async(job_id, file_paths))
        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"PDF processing failed for job {job_id}: {exc}")
        # Update job with error
        asyncio.run(_mark_job_failed(job_id, str(exc)))
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _mark_job_failed(job_id: str, error_message: str):
    """Mark job as failed with error message."""
    async with async_session() as session:
        await session.execute(
            update(Job).where(Job.id == job_id).values(
                status=JobStatus.FAILED.value,
                error_message=error_message
            )
        )
        await session.commit()


async def _process_pdf_async(job_id: str, file_paths: list):
    """Async helper for PDF processing."""
    async with async_session() as session:
        try:
            # Update status to processing
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.PROCESSING.value,
                    progress=5
                )
            )
            await session.commit()

            logger.info(f"Started processing {len(file_paths)} files for job {job_id}")

            total_questions = 0
            total_pages = 0
            all_questions_for_indexing = []

            # Process each PDF file
            for idx, file_path in enumerate(file_paths):
                try:
                    logger.info(f"Processing file {idx+1}/{len(file_paths)}: {file_path}")

                    # Calculate file hash
                    file_hash = _calculate_file_hash(file_path)
                    filename = os.path.basename(file_path)

                    # Create document record
                    document = Document(
                        job_id=job_id,
                        filename=filename,
                        file_hash=file_hash,
                    )
                    session.add(document)
                    await session.flush()  # Get document ID

                    # Extract text from PDF using LlamaCloud
                    logger.info(f"Extracting text from {filename}...")
                    extraction_result = await llama_service.extract_from_pdf(file_path)
                    
                    extracted_text = extraction_result.get("text", "")
                    pages = extraction_result.get("pages", [])
                    
                    # Extract exam metadata
                    logger.info(f"Extracting exam metadata from {filename}...")
                    exam_metadata = await llama_service.extract_exam_metadata(extracted_text)
                    
                    # Update document with metadata and page count
                    document.page_count = len(pages)
                    document.course_code = exam_metadata.course_code
                    document.course_name = exam_metadata.course_name
                    document.semester = exam_metadata.semester
                    document.exam_date = exam_metadata.exam_date
                    document.total_marks = exam_metadata.total_marks
                    document.duration_minutes = exam_metadata.duration_minutes
                    document.exam_type = exam_metadata.exam_type
                    total_pages += len(pages)

                    # Update progress
                    progress = 10 + (idx * 30 // len(file_paths))
                    await session.execute(
                        update(Job).where(Job.id == job_id).values(
                            progress=progress,
                            processed_pages=total_pages
                        )
                    )
                    await session.commit()

                    # Parse questions from extracted text by parts
                    logger.info(f"Parsing questions from {filename}...")
                    questions_by_parts = await llama_service.extract_questions_by_parts(extracted_text)
                    
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
                            has_or_option=1 if q_data.get("has_or_option", False) else 0,
                        )
                        session.add(question)
                        await session.flush()  # Get question ID

                        # Prepare for embedding and indexing
                        all_questions_for_indexing.append({
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
                        })

                    total_questions += len(questions_data)
                    await session.commit()

                    # Update progress
                    progress = 40 + (idx * 30 // len(file_paths))
                    await session.execute(
                        update(Job).where(Job.id == job_id).values(
                            progress=progress,
                            total_questions=total_questions
                        )
                    )
                    await session.commit()

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    # Continue with other files
                    continue

            # Generate embeddings and index in Qdrant
            if all_questions_for_indexing:
                logger.info(f"Generating embeddings for {len(all_questions_for_indexing)} questions...")
                
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
                for i, (q, embedding) in enumerate(zip(all_questions_for_indexing, embeddings)):
                    qdrant_points.append({
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
                    })

                # Index in Qdrant
                logger.info(f"Indexing {len(qdrant_points)} questions in Qdrant...")
                indexed_count = await qdrant_service.index_questions(qdrant_points)
                logger.info(f"Successfully indexed {indexed_count} questions")

                # Update qdrant_id in database
                for i, q in enumerate(all_questions_for_indexing):
                    await session.execute(
                        update(Question).where(Question.id == q["id"]).values(qdrant_id=i)
                    )
                await session.commit()

            # Mark job as completed
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.COMPLETED.value,
                    progress=100,
                    total_questions=total_questions,
                    processed_pages=total_pages
                )
            )
            await session.commit()

            logger.info(f"Job {job_id} completed successfully. Processed {total_questions} questions from {total_pages} pages")

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
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.FAILED.value,
                    error_message=str(e)
                )
            )
            await session.commit()
            raise


def _calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
