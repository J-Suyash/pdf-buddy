from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import os

from app.core.database import get_db
from app.models import Job, Document, JobStatus
from app.schemas import JobUploadResponse
from app.utils.exceptions import ValidationException

router = APIRouter(prefix="/api/v1", tags=["upload"])

UPLOAD_DIR = "/tmp/qp_uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = {"application/pdf"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=JobUploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload one or more PDF files for processing.
    Returns job_id and status URL.
    """
    if not files:
        raise ValidationException("No files provided")

    if len(files) > 10:
        raise ValidationException("Maximum 10 files per upload")

    # Validate files
    filenames = []
    file_paths = []

    for file in files:
        if file.content_type != "application/pdf":
            raise ValidationException(f"{file.filename} is not a PDF")

        # Read file to check size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise ValidationException(f"{file.filename} exceeds 50MB limit")

        filenames.append(file.filename)
        
        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        file_paths.append(file_path)

    try:
        # Create job record
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            status=JobStatus.QUEUED.value,
            file_names=",".join(filenames),
            progress=0,
        )
        db.add(job)
        await db.commit()

        return JobUploadResponse(
            job_id=job_id,
            status="queued",
            status_url=f"/api/v1/jobs/{job_id}",
            files=filenames,
        )

    except Exception as e:
        # Clean up uploaded files on error
        for fpath in file_paths:
            if os.path.exists(fpath):
                os.remove(fpath)
        raise HTTPException(status_code=500, detail=str(e))
