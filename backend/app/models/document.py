from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256
    file_path = Column(String(512), nullable=True)  # Path to stored PDF
    page_count = Column(Integer, default=0)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Exam metadata
    course_code = Column(String(50), nullable=True)  # e.g., "21CSE321J"
    course_name = Column(
        String(255), nullable=True
    )  # e.g., "SDWAN NETWORKING SOLUTIONS"
    semester = Column(String(50), nullable=True)  # e.g., "Fifth Semester"
    exam_date = Column(String(100), nullable=True)  # e.g., "NOVEMBER 2024"
    total_marks = Column(Integer, nullable=True)  # e.g., 75
    duration_minutes = Column(Integer, nullable=True)  # e.g., 180
    exam_type = Column(String(50), nullable=True)  # e.g., "End Semester", "Mid Term"

    # Relationships
    job = relationship("Job", back_populates="documents")
    questions = relationship(
        "Question", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document {self.id}: {self.filename}>"
