"""
NexusAI — Embedding Service
Generates embeddings using Ollama local models (100% FREE).
Uses nomic-embed-text (768 dimensions) by default.
"""

import hashlib
import logging
from typing import Dict, List, Optional

import ollama as ollama_client

from config import settings

logger = logging.getLogger("nexusai.embeddings")


class EmbeddingService:
    """Manages embedding generation with Ollama (free, local) and in-memory caching."""

    def __init__(self):
        self.model = settings.embedding_model
        self._cache: Dict[str, List[float]] = {}
        self.embedding_dimension = 768  # nomic-embed-text dimension

    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single text string using Ollama.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        cache_key = self._make_cache_key(text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        cleaned_text = text.replace("\n", " ").strip()
        if not cleaned_text:
            return [0.0] * self.embedding_dimension

        try:
            response = ollama_client.embed(
                model=self.model,
                input=cleaned_text,
            )
            embedding = response["embeddings"][0]
            self._cache[cache_key] = embedding
            return embedding

        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {str(e)}")
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")

    def generate_embeddings(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches using Ollama.

        Args:
            texts: List of text strings to embed.
            batch_size: Number of texts to embed per batch.

        Returns:
            List of embedding vectors in the same order as input.
        """
        if not texts:
            return []

        all_embeddings: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            cache_key = self._make_cache_key(text)
            if cache_key in self._cache:
                all_embeddings[i] = self._cache[cache_key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text.replace("\n", " ").strip())

        if uncached_texts:
            logger.info(
                f"🔄 Generating embeddings for {len(uncached_texts)} texts "
                f"({len(texts) - len(uncached_texts)} cached) using Ollama/{self.model}"
            )

            for batch_start in range(0, len(uncached_texts), batch_size):
                batch_end = min(batch_start + batch_size, len(uncached_texts))
                batch = uncached_texts[batch_start:batch_end]

                batch = [t if t else "empty" for t in batch]

                try:
                    # Ollama supports batch embedding
                    response = ollama_client.embed(
                        model=self.model,
                        input=batch,
                    )

                    for j, embedding in enumerate(response["embeddings"]):
                        global_idx = uncached_indices[batch_start + j]
                        all_embeddings[global_idx] = embedding

                        original_text = texts[global_idx]
                        cache_key = self._make_cache_key(original_text)
                        self._cache[cache_key] = embedding

                    logger.info(
                        f"✅ Batch {batch_start // batch_size + 1}: "
                        f"embedded {len(batch)} texts"
                    )

                except Exception as e:
                    logger.error(f"❌ Batch embedding failed: {str(e)}")
                    raise RuntimeError(f"Batch embedding generation failed: {str(e)}")

        result = []
        for emb in all_embeddings:
            if emb is None:
                result.append([0.0] * self.embedding_dimension)
            else:
                result.append(emb)

        return result

    def clear_cache(self) -> int:
        """Clear the embedding cache. Returns the number of entries cleared."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"🧹 Embedding cache cleared ({count} entries)")
        return count

    @staticmethod
    def _make_cache_key(text: str) -> str:
        """Create a cache key from text using MD5 hash."""
        normalized = text.strip().lower()
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()
