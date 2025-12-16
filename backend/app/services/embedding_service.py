import logging
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        logger.info("Initializing embedding service...")
        # Will load model when sentence-transformers is installed
        self.model = None
        self.embedding_dim = 384

    def _ensure_model(self):
        """Lazy load the model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading sentence transformer model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("sentence-transformers not installed, using stub")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate 384-dimensional embedding for text.
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dim

        self._ensure_model()
        
        if self.model is None:
            # Return zero vector if model not available
            return [0.0] * self.embedding_dim

        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    async def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return [[0.0] * self.embedding_dim] * len(texts)

        self._ensure_model()
        
        if self.model is None:
            # Return zero vectors if model not available
            return [[0.0] * self.embedding_dim] * len(texts)

        embeddings = self.model.encode(valid_texts, convert_to_tensor=False)
        return embeddings.tolist()


embedding_service = EmbeddingService()
