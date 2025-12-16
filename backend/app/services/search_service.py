from app.services.embedding_service import embedding_service
from app.core.qdrant import qdrant_service
from app.core.database import async_session
from app.models import Question
from sqlalchemy import select
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SearchService:
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Semantic search for questions.

        1. Generate embedding for query
        2. Search Qdrant for similar vectors
        3. Fetch full details from PostgreSQL
        4. Return results
        """
        try:
            logger.info(f"Searching for: {query}")

            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)

            # Search in Qdrant
            qdrant_results = await qdrant_service.search(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )

            if not qdrant_results:
                return {
                    "query": query,
                    "results": [],
                    "total": 0,
                    "took_ms": 0
                }

            # Fetch full question details from PostgreSQL
            async with async_session() as session:
                question_ids = [r["payload"]["question_id"] for r in qdrant_results if r["payload"].get("question_id")]
                
                if not question_ids:
                    return {
                        "query": query,
                        "results": [],
                        "total": 0,
                    }
                
                stmt = select(Question).where(Question.id.in_(question_ids))
                db_result = await session.execute(stmt)
                questions_map = {q.id: q for q in db_result.scalars().all()}

            # Combine results
            results = []
            for qdrant_result in qdrant_results:
                q_id = qdrant_result["payload"].get("question_id")
                if not q_id:
                    continue
                    
                question = questions_map.get(q_id)

                if question:
                    results.append({
                        "id": question.id,
                        "content": question.content,
                        "score": qdrant_result["score"],
                        "subject": question.subject,
                        "topic": question.topic,
                        "difficulty": question.difficulty,
                        "question_type": question.question_type,
                        "year": question.year,
                        "marks": question.marks,
                        "page_number": question.page_number,
                    })

            return {
                "query": query,
                "results": results,
                "total": len(results),
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise


search_service = SearchService()
