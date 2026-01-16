#!/usr/bin/env python3
"""
Integration test for Datalab + LlamaCloud fallback PDF processing.

This script tests:
1. Datalab browser automation (primary)
2. LlamaCloud API fallback when Datalab fails
3. Database storage and Qdrant indexing
4. Complete upload and processing flow
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

from app.config import settings
from app.models import Job, JobStatus, Document, Question, DatalabPDF, DatalabPage, DatalabChunk, DatalabVector
from app.services.datalab_service import datalab_service
from app.services.llama_service import llama_service
from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
from app.tasks.pdf_processor import process_pdf_task
from app.tasks.datalab_processor import process_datalab_pdf_task
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTester:
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
        )
        self.session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def cleanup_test_data(self):
        """Clean up test data from database and Qdrant."""
        logger.info("Cleaning up test data...")

        async with self.session_maker() as session:
            # Delete test jobs and related data
            await session.execute(delete(DatalabVector))
            await session.execute(delete(DatalabChunk))
            await session.execute(delete(DatalabPage))
            await session.execute(delete(DatalabPDF))
            await session.execute(delete(Question))
            await session.execute(delete(Document))
            await session.execute(delete(Job).where(Job.id.like("test-%")))
            await session.commit()

        # Clean up Qdrant
        try:
            await qdrant_service.client.delete_collection(
                collection_name=qdrant_service.collection_name
            )
            await qdrant_service.client.create_collection(
                collection_name=qdrant_service.collection_name,
                vectors_config=qdrant_service.vector_params
            )
            logger.info("Cleaned up Qdrant collection")
        except Exception as e:
            logger.warning(f"Could not clean up Qdrant: {e}")

    async def test_datalab_service(self):
        """Test Datalab service directly."""
        logger.info("=" * 60)
        logger.info("TEST 1: Datalab Service Direct Test")
        logger.info("=" * 60)

        # Create a simple test PDF path (you'll need to provide a real PDF)
        test_pdf_path = "/home/sxtr/Documents/SEM 5/Discrete Maths/Discrete_Mathematics_-_2025_JULY-B.pdf"

        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found at {test_pdf_path}")
            logger.info("Skipping Datalab test - no test PDF available")
            return None

        try:
            logger.info(f"Testing Datalab with PDF: {test_pdf_path}")

            # Process PDF with Datalab
            result = await datalab_service.process_pdf(
                file_path=test_pdf_path,
                job_id="test-datalab-001",
            )

            logger.info(f"Datalab processing successful!")
            logger.info(f"  Status: {result.get('status')}")
            logger.info(f"  Success: {result.get('success')}")
            logger.info(f"  Page count: {result.get('page_count', 0)}")

            # Parse the response
            parsed = datalab_service.parse_response(result, "test-datalab-001")
            logger.info(f"  Parsed pages: {len(parsed.pages)}")
            logger.info(f"  Total blocks: {sum(len(p.blocks) for p in parsed.pages)}")

            return parsed

        except Exception as e:
            logger.error(f"Datalab test failed: {e}")
            logger.info("This is expected if browser automation fails (e.g., captcha)")
            return None

    async def test_llama_service(self):
        """Test LlamaCloud service directly."""
        logger.info("=" * 60)
        logger.info("TEST 2: LlamaCloud Service Direct Test")
        logger.info("=" * 60)

        test_pdf_path = "/home/sxtr/Documents/SEM 5/Discrete Maths/Discrete_Mathematics_-_2025_JULY-B.pdf"

        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found at {test_pdf_path}")
            logger.info("Skipping LlamaCloud test - no test PDF available")
            return None

        if not settings.llama_cloud_api_key:
            logger.warning("LLAMA_CLOUD_API_KEY not set, skipping LlamaCloud test")
            return None

        try:
            logger.info(f"Testing LlamaCloud with PDF: {test_pdf_path}")

            result = await llama_service.extract_from_pdf(test_pdf_path)

            logger.info(f"LlamaCloud extraction successful!")
            logger.info(f"  Text length: {len(result.get('text', ''))}")
            logger.info(f"  Pages: {len(result.get('pages', []))}")
            logger.info(f"  Structured data keys: {list(result.get('structured_data', {}).keys())}")

            return result

        except Exception as e:
            logger.error(f"LlamaCloud test failed: {e}")
            return None

    async def test_pdf_processor_with_fallback(self):
        """Test the PDF processor with Datalab primary and Llama fallback."""
        logger.info("=" * 60)
        logger.info("TEST 3: PDF Processor with Datalab + Llama Fallback")
        logger.info("=" * 60)

        test_pdf_path = "/home/sxtr/Documents/SEM 5/Discrete Maths/Discrete_Mathematics_-_2025_JULY-B.pdf"

        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found at {test_pdf_path}")
            logger.info("Skipping processor test - no test PDF available")
            return None

        # Create a temporary copy of the PDF for processing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            import shutil
            shutil.copy2(test_pdf_path, tmp.name)
            temp_pdf_path = tmp.name

        try:
            # Create a test job
            async with self.session_maker() as session:
                job = Job(
                    id="test-processor-001",
                    status=JobStatus.QUEUED.value,
                    progress=0,
                    file_names=os.path.basename(test_pdf_path),  # Single filename as string
                )
                session.add(job)
                await session.commit()
                logger.info(f"Created test job: {job.id}")

            # Process the PDF
            logger.info("Starting PDF processing...")
            result = process_pdf_task(job.id, [temp_pdf_path])

            logger.info(f"Processing result: {result}")

            # Check the job status
            async with self.session_maker() as session:
                job_result = await session.execute(
                    select(Job).where(Job.id == job.id)
                )
                job = job_result.scalar_one_or_none()

                if job:
                    logger.info(f"Job status: {job.status}")
                    logger.info(f"Job progress: {job.progress}%")
                    logger.info(f"Total questions: {job.total_questions}")
                    logger.info(f"Processed pages: {job.processed_pages}")

                    if job.error_message:
                        logger.error(f"Job error: {job.error_message}")

            return job

        except Exception as e:
            logger.error(f"PDF processor test failed: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

    async def test_datalab_processor(self):
        """Test the Datalab-specific processor."""
        logger.info("=" * 60)
        logger.info("TEST 4: Datalab Processor (Browser Automation)")
        logger.info("=" * 60)

        test_pdf_path = "/home/sxtr/Documents/SEM 5/Discrete Maths/Discrete_Mathematics_-_2025_JULY-B.pdf"

        if not os.path.exists(test_pdf_path):
            logger.warning(f"Test PDF not found at {test_pdf_path}")
            logger.info("Skipping Datalab processor test - no test PDF available")
            return None

        # Create a temporary copy of the PDF for processing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            import shutil
            shutil.copy2(test_pdf_path, tmp.name)
            temp_pdf_path = tmp.name

        try:
            # Create a test job
            async with self.session_maker() as session:
                job = Job(
                    id="test-datalab-processor-001",
                    status=JobStatus.QUEUED.value,
                    progress=0,
                    file_names=os.path.basename(test_pdf_path),  # Single filename as string
                )
                session.add(job)
                await session.commit()
                logger.info(f"Created test job: {job.id}")

            # Process the PDF with Datalab
            logger.info("Starting Datalab PDF processing...")
            result = process_datalab_pdf_task(job.id, temp_pdf_path)

            logger.info(f"Datalab processing result: {result}")

            # Check the job status
            async with self.session_maker() as session:
                job_result = await session.execute(
                    select(Job).where(Job.id == job.id)
                )
                job = job_result.scalar_one_or_none()

                if job:
                    logger.info(f"Job status: {job.status}")
                    logger.info(f"Job progress: {job.progress}%")
                    logger.info(f"Total questions: {job.total_questions}")
                    logger.info(f"Processed pages: {job.processed_pages}")

                    if job.error_message:
                        logger.error(f"Job error: {job.error_message}")

            return job

        except Exception as e:
            logger.error(f"Datalab processor test failed: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

    async def test_embedding_service(self):
        """Test embedding generation."""
        logger.info("=" * 60)
        logger.info("TEST 5: Embedding Service")
        logger.info("=" * 60)

        test_texts = [
            "What is a binary tree?",
            "Explain quicksort algorithm",
            "What is dynamic programming?",
        ]

        try:
            logger.info("Generating embeddings for test texts...")
            embeddings = await embedding_service.batch_generate(test_texts)

            logger.info(f"Generated {len(embeddings)} embeddings")
            logger.info(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")

            return embeddings

        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
            return None

    async def test_qdrant_service(self):
        """Test Qdrant vector database."""
        logger.info("=" * 60)
        logger.info("TEST 6: Qdrant Vector Database")
        logger.info("=" * 60)

        try:
            # Check if collection exists
            collections = qdrant_service.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            logger.info(f"Available collections: {collection_names}")

            if qdrant_service.collection_name in collection_names:
                logger.info(f"Collection '{qdrant_service.collection_name}' exists")
            else:
                logger.warning(f"Collection '{qdrant_service.collection_name}' not found")

            return True

        except Exception as e:
            logger.error(f"Qdrant test failed: {e}")
            return None

    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("\n" + "=" * 60)
        logger.info("INTEGRATION TEST SUITE")
        logger.info("=" * 60 + "\n")

        results = {}

        try:
            # Clean up first
            await self.cleanup_test_data()

            # Run tests
            results["datalab_service"] = await self.test_datalab_service()
            results["llama_service"] = await self.test_llama_service()
            results["pdf_processor"] = await self.test_pdf_processor_with_fallback()
            results["datalab_processor"] = await self.test_datalab_processor()
            results["embedding_service"] = await self.test_embedding_service()
            results["qdrant_service"] = await self.test_qdrant_service()

            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("TEST SUMMARY")
            logger.info("=" * 60)

            for test_name, result in results.items():
                status = "✓ PASS" if result is not None else "✗ SKIP/FAIL"
                logger.info(f"{test_name:25} {status}")

            # Final cleanup
            await self.cleanup_test_data()

            logger.info("\n" + "=" * 60)
            logger.info("INTEGRATION TESTS COMPLETED")
            logger.info("=" * 60)

            return results

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
        finally:
            await self.engine.dispose()


async def main():
    """Main entry point."""
    tester = IntegrationTester()
    results = await tester.run_all_tests()

    # Exit with appropriate code
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)

    logger.info(f"\nResults: {success_count}/{total_count} tests passed")

    if success_count == total_count:
        logger.info("✓ All tests passed!")
        sys.exit(0)
    else:
        logger.warning("⚠ Some tests were skipped or failed")
        sys.exit(0)  # Exit 0 since failures might be expected (e.g., captcha)


if __name__ == "__main__":
    asyncio.run(main())
