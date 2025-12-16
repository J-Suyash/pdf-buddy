from pydantic import BaseModel, Field
from typing import Optional


class QuestionResponse(BaseModel):
    id: str
    content: str
    subject: Optional[str]
    topic: Optional[str]
    difficulty: Optional[str]
    question_type: Optional[str]
    year: Optional[int]
    marks: Optional[int]
    page_number: Optional[int]
    score: Optional[float] = None  # For search results

    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[dict] = None
