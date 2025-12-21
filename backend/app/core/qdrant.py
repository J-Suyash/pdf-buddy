from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
import logging
from typing import List, Dict, Optional
import uuid

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host, port=settings.qdrant_port, timeout=30
        )
        self.collection_name = "questions"
        self.datalab_collection_name = (
            "datalab_chunks"  # Separate collection for datalab
        )
        self.vector_size = 384
        self._ensure_collection()
        self._ensure_datalab_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            logger.info(f"Creating collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    def _ensure_datalab_collection(self):
        """Create datalab collection if it doesn't exist."""
        try:
            self.client.get_collection(self.datalab_collection_name)
            logger.info(f"Collection '{self.datalab_collection_name}' already exists")
        except:
            logger.info(f"Creating collection '{self.datalab_collection_name}'...")
            self.client.create_collection(
                collection_name=self.datalab_collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    async def index_questions(self, questions: List[Dict]) -> int:
        """
        Index questions with embeddings into Qdrant.

        Args:
            questions: List of dicts with id, vector (embedding), question_id, text, metadata

        Returns:
            Number of indexed points
        """
        if not questions:
            return 0

        points = []
        for idx, q in enumerate(questions):
            point = PointStruct(
                id=idx,  # Simple sequential ID for MVP
                vector=q.get("vector", [0.0] * self.vector_size),
                payload={
                    "question_id": q.get("question_id"),
                    "text": q.get("text", ""),
                    "subject": q.get("subject"),
                    "topic": q.get("topic"),
                    "difficulty": q.get("difficulty"),
                    "question_type": q.get("question_type"),
                    "year": q.get("year"),
                    "marks": q.get("marks"),
                    "document_id": q.get("document_id"),
                    "page_number": q.get("page_number"),
                },
            )
            points.append(point)

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Indexed {len(points)} questions into Qdrant")
            return len(points)
        except Exception as e:
            logger.error(f"Failed to index questions: {e}")
            raise

    async def search(
        self, query_vector: List[float], limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar questions using semantic similarity.
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
            )

            return [
                {"id": result.id, "score": result.score, "payload": result.payload}
                for result in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def delete_collection(self):
        """Delete collection for testing/reset."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except:
            pass

    async def index_datalab_chunks(self, chunks: List[Dict]) -> int:
        """
        Index datalab chunks with embeddings into Qdrant.

        Args:
            chunks: List of dicts with id (UUID string), vector, and payload

        Returns:
            Number of indexed points
        """
        if not chunks:
            return 0

        points = []
        for chunk in chunks:
            point = PointStruct(
                id=chunk.get("id"),  # UUID string
                vector=chunk.get("vector", [0.0] * self.vector_size),
                payload=chunk.get("payload", {}),
            )
            points.append(point)

        try:
            self.client.upsert(
                collection_name=self.datalab_collection_name, points=points
            )
            logger.info(f"Indexed {len(points)} datalab chunks into Qdrant")
            return len(points)
        except Exception as e:
            logger.error(f"Failed to index datalab chunks: {e}")
            raise

    async def search_datalab_chunks(
        self, query_vector: List[float], limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar datalab chunks using semantic similarity.
        """
        try:
            results = self.client.search(
                collection_name=self.datalab_collection_name,
                query_vector=query_vector,
                limit=limit,
            )

            return [
                {"id": result.id, "score": result.score, "payload": result.payload}
                for result in results
            ]
        except Exception as e:
            logger.error(f"Datalab search failed: {e}")
            raise


qdrant_service = QdrantService()
