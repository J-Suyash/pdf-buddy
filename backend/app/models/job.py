from sqlalchemy import Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(20), default=JobStatus.QUEUED.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    file_names = Column(String(500), nullable=False)  # Comma-separated
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    total_questions = Column(Integer, default=0)
    processed_pages = Column(Integer, default=0)

    # Relationships
    documents = relationship("Document", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.id}: {self.status}>"
