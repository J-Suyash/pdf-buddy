from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    qdrant_id = Column(Integer, nullable=True)  # Qdrant point ID

    # Part information
    part = Column(String(10), nullable=True)  # "A", "B", "C"
    part_marks = Column(Integer, nullable=True)  # marks for this part
    question_number = Column(String(20), nullable=True)  # "21", "21.a", "1"
    unit = Column(Integer, nullable=True)  # 1-5, based on question numbering

    # MCQ specific
    is_mcq = Column(Integer, default=0)  # SQLite doesn't have Boolean, using Integer
    options = Column(JSON, nullable=True)  # {"A": "...", "B": "...", ...}
    correct_answer = Column(String(10), nullable=True)  # if available

    # Metadata
    subject = Column(String(100), nullable=True)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    question_type = Column(String(50), nullable=True)  # descriptive, mcq, etc
    year = Column(Integer, nullable=True)
    marks = Column(Integer, nullable=True)
    page_number = Column(Integer, nullable=True)

    # Additional flags
    is_mandatory = Column(Integer, default=1)  # vs "Answer ANY ONE"
    has_or_option = Column(Integer, default=0)  # has (OR) alternative

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.id}: {self.subject}>"

    @property
    def course_code(self):
        return self.document.course_code if self.document else None

    @property
    def course_name(self):
        return self.document.course_name if self.document else None

    @property
    def exam_date(self):
        return self.document.exam_date if self.document else None
