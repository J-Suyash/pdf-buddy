from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from datetime import datetime
import uuid

from app.core.database import Base


class QuestionReview(Base):
    """Track questions marked for review by users."""

    __tablename__ = "question_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    # In future, add user_id when authentication is implemented
    # user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    marked_for_review = Column(Boolean, default=True, nullable=False)
    notes = Column(String(1000), nullable=True)  # Optional notes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<QuestionReview {self.id}: Question {self.question_id}>"
