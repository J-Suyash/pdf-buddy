"""
Datalab OCR API endpoints.

This module provides endpoints for uploading PDFs to be processed
using Datalab's OCR service via browser automation.

Note: Only ONE PDF at a time is supported due to the browser automation requirements.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
import os
import logging

from app.core.database import get_db
from app.models import Job, JobStatus, DatalabPDF, DatalabPage, DatalabChunk
from app.schemas.job import JobUploadResponse
from app.utils.exceptions import ValidationException
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datalab", tags=["datalab"])

UPLOAD_DIR = settings.upload_dir
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=JobUploadResponse)
async def upload_datalab_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a single PDF file for Datalab OCR processing.

    Unlike the regular upload endpoint, this only accepts ONE PDF at a time
    due to the browser automation requirements of Datalab.

    The processing includes:
    1. Browser-based upload to datalab.to
    2. Automatic Turnstile captcha solving
    3. Polling for results
    4. Storing pages and chunks in database
    5. Generating embeddings for vector search

    Returns:
        JobUploadResponse with job_id and status_url
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise ValidationException(f"{file.filename} is not a PDF file")

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValidationException(
            f"{file.filename} exceeds {settings.max_file_size_mb}MB limit"
        )

    # Save file temporarily
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        # Create job record
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            status=JobStatus.QUEUED.value,
            file_names=file.filename,  # Single file
            progress=0,
        )
        db.add(job)
        await db.commit()

        # Trigger Celery task for background processing
        from app.tasks.datalab_processor import process_datalab_pdf_task

        process_datalab_pdf_task.delay(job_id, file_path)

        logger.info(f"Datalab job {job_id} created and queued for processing")

        return JobUploadResponse(
            job_id=job_id,
            status="queued",
            status_url=f"/api/v1/jobs/{job_id}",
            files=[file.filename],
        )

    except Exception as e:
        # Clean up uploaded file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Failed to create datalab job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdfs")
async def list_datalab_pdfs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List all PDFs processed with Datalab OCR.
    """
    result = await db.execute(
        select(DatalabPDF)
        .order_by(DatalabPDF.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    pdfs = result.scalars().all()

    return {
        "pdfs": [
            {
                "id": pdf.id,
                "job_id": pdf.job_id,
                "name": pdf.name,
                "num_pages": pdf.num_pages,
                "runtime_seconds": pdf.runtime_seconds,
                "created_at": pdf.created_at.isoformat() if pdf.created_at else None,
            }
            for pdf in pdfs
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/pdfs/{pdf_id}")
async def get_datalab_pdf(
    pdf_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific Datalab-processed PDF including all pages.
    """
    result = await db.execute(select(DatalabPDF).where(DatalabPDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    # Get pages
    pages_result = await db.execute(
        select(DatalabPage)
        .where(DatalabPage.pdf_id == pdf_id)
        .order_by(DatalabPage.page_num)
    )
    pages = pages_result.scalars().all()

    return {
        "id": pdf.id,
        "job_id": pdf.job_id,
        "name": pdf.name,
        "file_path": pdf.file_path,
        "num_pages": pdf.num_pages,
        "markdown": pdf.markdown,
        "html": pdf.html,
        "runtime_seconds": pdf.runtime_seconds,
        "created_at": pdf.created_at.isoformat() if pdf.created_at else None,
        "pages": [
            {
                "id": page.id,
                "page_num": page.page_num,
                "num_blocks": page.num_blocks,
                "markdown": page.markdown,
            }
            for page in pages
        ],
    }


@router.get("/pdfs/{pdf_id}/file")
async def get_datalab_pdf_file(
    pdf_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the original PDF file.
    """
    result = await db.execute(select(DatalabPDF).where(DatalabPDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if not pdf.file_path or not os.path.exists(pdf.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        pdf.file_path,
        media_type="application/pdf",
        filename=pdf.name,
    )


@router.get("/pdfs/{pdf_id}/pages/{page_num}")
async def get_datalab_page(
    pdf_id: str,
    page_num: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific page including all chunks.
    """
    # Get page
    result = await db.execute(
        select(DatalabPage)
        .where(DatalabPage.pdf_id == pdf_id)
        .where(DatalabPage.page_num == page_num)
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Get chunks for this page
    chunks_result = await db.execute(
        select(DatalabChunk).where(DatalabChunk.page_id == page.id)
    )
    chunks = chunks_result.scalars().all()

    return {
        "id": page.id,
        "pdf_id": pdf_id,
        "page_num": page.page_num,
        "num_blocks": page.num_blocks,
        "markdown": page.markdown,
        "html": page.html,
        "chunks": [
            {
                "id": chunk.id,
                "block_id": chunk.block_id,
                "block_type": chunk.block_type,
                "text": chunk.text,
                "bbox": chunk.bbox,
                "polygon": chunk.polygon,
                "images": chunk.images,
            }
            for chunk in chunks
        ],
    }


@router.get("/chunks/{chunk_id}")
async def get_datalab_chunk(
    chunk_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific chunk.
    """
    result = await db.execute(select(DatalabChunk).where(DatalabChunk.id == chunk_id))
    chunk = result.scalar_one_or_none()

    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {
        "id": chunk.id,
        "pdf_id": chunk.pdf_id,
        "page_id": chunk.page_id,
        "block_id": chunk.block_id,
        "block_type": chunk.block_type,
        "text": chunk.text,
        "html": chunk.html,
        "bbox": chunk.bbox,
        "polygon": chunk.polygon,
        "images": chunk.images,
        "section_hierarchy": chunk.section_hierarchy,
    }


@router.get("/search")
async def search_datalab_chunks(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search Datalab chunks using semantic similarity.
    """
    from app.services.embedding_service import embedding_service
    from app.core.qdrant import qdrant_service

    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(q)

    # Search in Qdrant
    results = await qdrant_service.search_datalab_chunks(
        query_vector=query_embedding,
        limit=limit,
    )

    # Fetch full chunk data from database
    chunk_ids = [r["payload"].get("chunk_id") for r in results if r.get("payload")]

    if not chunk_ids:
        return {"query": q, "results": [], "total": 0}

    chunks_result = await db.execute(
        select(DatalabChunk).where(DatalabChunk.id.in_(chunk_ids))
    )
    chunks = {chunk.id: chunk for chunk in chunks_result.scalars().all()}

    # Combine with scores
    enriched_results = []
    for r in results:
        chunk_id = r["payload"].get("chunk_id")
        chunk = chunks.get(chunk_id)
        if chunk:
            enriched_results.append(
                {
                    "id": chunk.id,
                    "score": r["score"],
                    "text": chunk.text,
                    "block_type": chunk.block_type,
                    "pdf_id": chunk.pdf_id,
                    "page_id": chunk.page_id,
                    "page_num": r["payload"].get("page_num"),
                }
            )

    return {
        "query": q,
        "results": enriched_results,
        "total": len(enriched_results),
    }
