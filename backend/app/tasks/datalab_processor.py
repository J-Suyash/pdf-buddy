"""
Celery task for processing PDFs using Datalab OCR.

This task handles:
1. Browser-based PDF upload to datalab.to
2. Captcha solving
3. Result polling
4. Database storage of pages and chunks
5. Embedding generation and Qdrant indexing
"""

from app.tasks.celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.config import settings
from app.models import (
    Job,
    JobStatus,
    DatalabPDF,
    DatalabPage,
    DatalabChunk,
    DatalabVector,
)
from app.services.datalab_service import datalab_service
from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
import logging
import hashlib
import os
import shutil
import uuid

logger = logging.getLogger(__name__)

# Ensure storage directories exist
PERMANENT_STORAGE_DIR = settings.permanent_storage_dir
DATALAB_STORAGE_DIR = settings.datalab_storage_dir
os.makedirs(PERMANENT_STORAGE_DIR, exist_ok=True)
os.makedirs(DATALAB_STORAGE_DIR, exist_ok=True)


@celery_app.task(
    bind=True, max_retries=0, name="process_datalab_pdf_task", queue="datalab"
)
def process_datalab_pdf_task(self, job_id: str, file_path: str):
    """
    Process a single PDF file using Datalab OCR.

    Unlike the LlamaCloud task, this only processes one PDF at a time
    due to the browser automation requirements.

    Progress updates:
    - 5%: Job started, browser launching
    - 15%: Page loaded, file upload initiated
    - 25%: Turnstile captcha solving
    - 35%: PDF parsing initiated
    - 50%: Polling for results
    - 70%: Results received, parsing response
    - 85%: Storing pages and chunks in DB
    - 95%: Generating embeddings
    - 100%: Complete
    """
    import asyncio

    # Create a new engine for this task
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    task_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def _run_task():
        try:
            await _process_datalab_pdf_async(job_id, file_path, task_session_maker)
        finally:
            await engine.dispose()

    try:
        asyncio.run(_run_task())
        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"Datalab PDF processing failed for job {job_id}: {exc}")

        # Mark job as failed
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

        # Don't retry - captcha failures shouldn't auto-retry
        raise


async def _mark_job_failed(job_id: str, error_message: str, session_maker):
    """Mark job as failed with error message."""
    async with session_maker() as session:
        await session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.FAILED.value, error_message=error_message)
        )
        await session.commit()


async def _process_datalab_pdf_async(job_id: str, file_path: str, session_maker):
    """Async helper for Datalab PDF processing."""
    async with session_maker() as session:
        try:
            # Progress callback for the service
            async def update_progress(progress: int, message: str):
                await session.execute(
                    update(Job)
                    .where(Job.id == job_id)
                    .values(progress=progress, error_message=message)
                )
                await session.commit()

            # Update status to processing
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(status=JobStatus.PROCESSING.value, progress=5)
            )
            await session.commit()

            logger.info(f"Started Datalab processing for job {job_id}: {file_path}")

            # Calculate file hash
            file_hash = _calculate_file_hash(file_path)
            filename = os.path.basename(file_path)

            # Copy to permanent storage
            permanent_file_path = os.path.join(
                PERMANENT_STORAGE_DIR, f"{file_hash}_{filename}"
            )
            shutil.copy2(file_path, permanent_file_path)
            logger.info(f"Copied file to permanent storage: {permanent_file_path}")

            # Sync progress callback wrapper
            def sync_progress_callback(progress: int, message: str):
                # We can't easily call async from sync callback in zendriver handlers
                # So we'll log progress instead - the main progress updates happen in the task
                logger.info(f"[Job {job_id}] Progress: {progress}% - {message}")

            # Process PDF with Datalab
            raw_result = await datalab_service.process_pdf(
                file_path=file_path,
                job_id=job_id,
                progress_callback=sync_progress_callback,
            )

            # Update progress - results received
            await session.execute(
                update(Job).where(Job.id == job_id).values(progress=70)
            )
            await session.commit()

            # Parse the response
            logger.info(f"Parsing Datalab response for job {job_id}")
            parsed_result = datalab_service.parse_response(raw_result, job_id)

            if not parsed_result.success:
                raise RuntimeError(f"Datalab processing failed: {parsed_result.status}")

            # Update progress - storing in DB
            await session.execute(
                update(Job).where(Job.id == job_id).values(progress=85)
            )
            await session.commit()

            # Create DatalabPDF record
            datalab_pdf = DatalabPDF(
                id=str(uuid.uuid4()),
                job_id=job_id,
                name=filename,
                file_hash=file_hash,
                file_path=permanent_file_path,
                num_pages=parsed_result.page_count,
                markdown=parsed_result.markdown,
                html=parsed_result.html,
                runtime_seconds=parsed_result.runtime_seconds,
            )
            session.add(datalab_pdf)
            await session.flush()

            # Store pages and chunks
            all_chunks_for_indexing = []

            for parsed_page in parsed_result.pages:
                # Create DatalabPage record
                page = DatalabPage(
                    id=str(uuid.uuid4()),
                    pdf_id=datalab_pdf.id,
                    page_num=parsed_page.page_num,
                    markdown=parsed_page.markdown,
                    html=parsed_page.html,
                    num_blocks=parsed_page.num_blocks,
                )
                session.add(page)
                await session.flush()

                # Create DatalabChunk records for each block
                for block in parsed_page.blocks:
                    chunk = DatalabChunk(
                        id=str(uuid.uuid4()),
                        pdf_id=datalab_pdf.id,
                        page_id=page.id,
                        block_id=block.block_id,
                        block_type=block.block_type,
                        text=block.text,
                        html=block.html,
                        images=block.images if block.images else None,
                        bbox=block.bbox if block.bbox else None,
                        polygon=block.polygon if block.polygon else None,
                        section_hierarchy=block.section_hierarchy
                        if block.section_hierarchy
                        else None,
                    )
                    session.add(chunk)
                    await session.flush()

                    # Only index chunks that have meaningful text
                    if block.text and len(block.text.strip()) > 10:
                        all_chunks_for_indexing.append(
                            {
                                "chunk_id": chunk.id,
                                "pdf_id": datalab_pdf.id,
                                "page_id": page.id,
                                "text": block.text,
                                "block_type": block.block_type,
                                "page_num": parsed_page.page_num,
                            }
                        )

            await session.commit()
            logger.info(
                f"Stored {len(parsed_result.pages)} pages with chunks for job {job_id}"
            )

            # Generate embeddings and index in Qdrant
            if all_chunks_for_indexing:
                # Update progress
                await session.execute(
                    update(Job).where(Job.id == job_id).values(progress=95)
                )
                await session.commit()

                logger.info(
                    f"Generating embeddings for {len(all_chunks_for_indexing)} chunks..."
                )

                # Generate embeddings in batch
                texts = [c["text"] for c in all_chunks_for_indexing]
                embeddings = await embedding_service.batch_generate(texts)

                # Prepare data for Qdrant (using separate collection for datalab)
                qdrant_points = []
                for i, (chunk_data, embedding) in enumerate(
                    zip(all_chunks_for_indexing, embeddings)
                ):
                    qdrant_id = str(uuid.uuid4())
                    qdrant_points.append(
                        {
                            "id": qdrant_id,
                            "vector": embedding,
                            "payload": {
                                "chunk_id": chunk_data["chunk_id"],
                                "pdf_id": chunk_data["pdf_id"],
                                "page_id": chunk_data["page_id"],
                                "text": chunk_data["text"],
                                "block_type": chunk_data["block_type"],
                                "page_num": chunk_data["page_num"],
                            },
                        }
                    )

                    # Create DatalabVector record
                    vector = DatalabVector(
                        id=str(uuid.uuid4()),
                        chunk_id=chunk_data["chunk_id"],
                        pdf_id=chunk_data["pdf_id"],
                        page_id=chunk_data["page_id"],
                        qdrant_id=qdrant_id,
                    )
                    session.add(vector)

                await session.commit()

                # Index in Qdrant using datalab-specific collection
                logger.info(f"Indexing {len(qdrant_points)} chunks in Qdrant...")
                indexed_count = await qdrant_service.index_datalab_chunks(qdrant_points)
                logger.info(f"Successfully indexed {indexed_count} chunks")

            # Mark job as completed
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(
                    status=JobStatus.COMPLETED.value,
                    progress=100,
                    processed_pages=parsed_result.page_count,
                    total_questions=len(
                        all_chunks_for_indexing
                    ),  # Reusing field for chunk count
                    error_message=None,
                )
            )
            await session.commit()

            logger.info(
                f"Job {job_id} completed successfully. "
                f"Processed {parsed_result.page_count} pages, {len(all_chunks_for_indexing)} chunks"
            )

            # Clean up temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error processing Datalab PDF: {e}")
            await session.execute(
                update(Job)
                .where(Job.id == job_id)
                .values(status=JobStatus.FAILED.value, error_message=str(e))
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
