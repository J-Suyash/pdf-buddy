from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os

from app.core.database import get_db
from app.models import Document, Question
from app.schemas.question import QuestionResponse

router = APIRouter(tags=["documents"])


@router.get("/documents/{document_id}")
async def get_document_details(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get document details with all associated questions."""
    # Fetch document with questions
    stmt = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.questions))
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Format response
    return {
        "id": str(document.id),
        "filename": document.filename,
        "file_hash": document.file_hash,
        "page_count": document.page_count,
        "course_code": document.course_code,
        "course_name": document.course_name,
        "semester": document.semester,
        "exam_date": document.exam_date,
        "total_marks": document.total_marks,
        "duration_minutes": document.duration_minutes,
        "exam_type": document.exam_type,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "questions": [
            {
                "id": str(q.id),
                "content": q.content,
                "document_id": str(q.document_id),
                "part": q.part,
                "part_marks": q.part_marks,
                "question_number": q.question_number,
                "unit": q.unit,
                "is_mcq": bool(q.is_mcq),
                "options": q.options,
                "correct_answer": q.correct_answer,
                "subject": q.subject,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question_type": q.question_type,
                "year": q.year,
                "marks": q.marks,
                "is_mandatory": bool(q.is_mandatory),
                "has_or_option": bool(q.has_or_option),
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in document.questions
        ],
    }


@router.get("/documents/{document_id}/pdf")
async def get_document_pdf(document_id: str, db: AsyncSession = Depends(get_db)):
    """Serve the original PDF file for a document."""
    # Fetch document to get file path
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if file_path is stored and file exists
    if document.file_path and os.path.exists(document.file_path):
        pdf_path = document.file_path
    else:
        raise HTTPException(
            status_code=404,
            detail="PDF file not found. The file may not have been saved or was deleted.",
        )

    return FileResponse(
        pdf_path, media_type="application/pdf", filename=document.filename
    )

    pdf_path = potential_files[0]

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path, media_type="application/pdf", filename=document.filename
    )
