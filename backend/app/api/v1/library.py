from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.models import Question, Document
from app.schemas.question import QuestionResponse

router = APIRouter()


@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    course_code: Optional[str] = None,
    year: Optional[str] = None,
    exam_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all questions from the database with optional filtering."""
    query = (
        select(Question)
        .join(Document)
        .options(selectinload(Question.document))
        .order_by(Question.created_at.desc())
    )

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Question.content.ilike(search_term),
                Question.subject.ilike(search_term),
                Document.course_name.ilike(search_term),
                Document.course_code.ilike(search_term),
            )
        )

    if course_code:
        query = query.where(Document.course_code.ilike(f"%{course_code}%"))

    if year:
        query = query.where(Document.exam_date.ilike(f"%{year}%"))

    if exam_type:
        query = query.where(Document.exam_type == exam_type)

    result = await db.execute(query.offset(skip).limit(limit))
    questions = result.scalars().all()
    return questions


@router.get("/documents")
async def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    course_code: Optional[str] = None,
    year: Optional[str] = None,
    exam_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all documents from the database with optional filtering."""

    query = select(Document).order_by(Document.created_at.desc())

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Document.filename.ilike(search_term))
            | (Document.course_name.ilike(search_term))
            | (Document.course_code.ilike(search_term))
        )

    if course_code:
        query = query.where(Document.course_code.ilike(f"%{course_code}%"))

    if year:
        query = query.where(Document.exam_date.ilike(f"%{year}%"))

    if exam_type:
        query = query.where(Document.exam_type == exam_type)

    result = await db.execute(query.offset(skip).limit(limit))
    documents = result.scalars().all()

    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "file_hash": doc.file_hash,
            "page_count": doc.page_count,
            "course_code": doc.course_code,
            "course_name": doc.course_name,
            "semester": doc.semester,
            "exam_date": doc.exam_date,
            "total_marks": doc.total_marks,
            "duration_minutes": doc.duration_minutes,
            "exam_type": doc.exam_type,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }
        for doc in documents
    ]
