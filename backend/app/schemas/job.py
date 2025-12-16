from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.job import JobStatus


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    file_names: str
    progress: int = Field(ge=0, le=100)
    total_questions: int = 0
    processed_pages: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class JobUploadResponse(BaseModel):
    job_id: str
    status: str
    status_url: str
    files: List[str]
