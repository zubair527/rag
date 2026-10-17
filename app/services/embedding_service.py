"""Embedding service using sentence-transformers"""
import hashlib
import json
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import redis
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating embeddings"""

    def __init__(self):
        self.model_name = settings.embedding_model_name
        self.batch_size = settings.embedding_batch_size
        self.model: Optional[SentenceTransformer] = None
        self.redis_client: Optional[redis.Redis] = None

    def initialize(self) -> None:
        """Initialize embedding model and cache"""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("Embedding model loaded successfully")

        # Initialize Redis cache
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=False,
                socket_connect_timeout=5,
            )
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}. Continuing without cache.")
            self.redis_client = None

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"embedding:{self.model_name}:{text_hash}"

    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        if not self.redis_client:
            return None

        try:
            key = self._get_cache_key(text)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")

        return None

    def _save_to_cache(self, text: str, embedding: List[float]) -> None:
        """Save embedding to cache"""
        if not self.redis_client:
            return

        try:
            key = self._get_cache_key(text)
            self.redis_client.setex(
                key,
                settings.redis_cache_ttl,
                json.dumps(embedding)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {e}")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        # Check cache first
        cached_embedding = self._get_from_cache(text)
        if cached_embedding:
            return cached_embedding

        # Generate embedding
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        embedding = self.model.encode(text, convert_to_numpy=True)
        embedding_list = embedding.tolist()

        # Save to cache
        self._save_to_cache(text, embedding_list)

        return embedding_list

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache for each text
        for idx, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached:
                embeddings.append(cached)
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(idx)

        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.model.encode(
                uncached_texts,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            for idx, text, embedding in zip(uncached_indices, uncached_texts, new_embeddings):
                embedding_list = embedding.tolist()
                embeddings[idx] = embedding_list
                self._save_to_cache(text, embedding_list)

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return settings.embedding_dimension


# Global embedding service instance
embedding_service = EmbeddingService()