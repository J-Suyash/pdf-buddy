from app.tasks.celery_app import celery_app
from app.core.database import async_session
from app.models import Job, JobStatus
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, name="process_pdf_task")
def process_pdf_task(self, job_id: str, file_paths: list):
    """
    Process PDF files:
    1. Update job status to processing
    2. Extract text from PDF (stub for now)
    3. Store questions in database
    4. Trigger embedding task
    5. Update job status to completed
    """
    import asyncio

    try:
        # Run async function
        asyncio.run(_process_pdf_async(job_id, file_paths))
        return {"status": "completed", "job_id": job_id}

    except Exception as exc:
        logger.error(f"PDF processing failed for job {job_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _process_pdf_async(job_id: str, file_paths: list):
    """Async helper for PDF processing."""
    async with async_session() as session:
        try:
            # Update status to processing
            from sqlalchemy import select, update
            await session.execute(
                update(Job).where(Job.id == job_id).values(status=JobStatus.PROCESSING.value)
            )
            await session.commit()

            logger.info(f"Started processing {len(file_paths)} files for job {job_id}")

            # TODO: Implement LlamaCloud extraction
            # For now, just mark as completed

            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status=JobStatus.COMPLETED.value,
                    progress=100
                )
            )
            await session.commit()

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
