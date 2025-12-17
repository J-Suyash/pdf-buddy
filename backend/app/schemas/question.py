from pydantic import BaseModel, Field
from typing import Optional, Dict


class QuestionResponse(BaseModel):
    id: str
    content: str
    
    # Part information
    part: Optional[str] = None
    part_marks: Optional[int] = None
    question_number: Optional[str] = None
    unit: Optional[int] = None  # 1-5
    
    # MCQ fields
    is_mcq: bool = False
    options: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = None
    
    # Metadata
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    year: Optional[int] = None
    marks: Optional[int] = None
    page_number: Optional[int] = None
    score: Optional[float] = None  # For search results
    
    # Document Metadata
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    exam_date: Optional[str] = None
    
    # Additional flags
    is_mandatory: bool = True
    has_or_option: bool = False

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[dict] = None


class ExamPaperMetadata(BaseModel):
    """Metadata extracted from exam paper."""
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    semester: Optional[str] = None
    exam_date: Optional[str] = None
    total_marks: Optional[int] = None
    duration_minutes: Optional[int] = None
    exam_type: Optional[str] = None
