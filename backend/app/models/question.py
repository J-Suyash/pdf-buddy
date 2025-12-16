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

    # Metadata
    subject = Column(String(100), nullable=True)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    question_type = Column(String(50), nullable=True)  # descriptive, mcq, etc
    year = Column(Integer, nullable=True)
    marks = Column(Integer, nullable=True)
    page_number = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.id}: {self.subject}>"
