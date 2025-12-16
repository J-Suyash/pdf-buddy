from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import logging

from app.services.search_service import search_service
from app.utils.exceptions import ValidationException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search")
async def search(
    q: str = Query(..., min_length=3, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    year: Optional[int] = Query(None, description="Filter by year"),
):
    """
    Semantic search for questions.

    Returns top matching questions based on semantic similarity.
    """
    try:
        filters = {}
        if subject:
            filters["subject"] = subject
        if year:
            filters["year"] = year

        results = await search_service.semantic_search(
            query=q,
            limit=limit,
            filters=filters if filters else None
        )

        return results

    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
