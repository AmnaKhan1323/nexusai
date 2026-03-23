"""
NexusAI — Vector Store Service
ChromaDB integration for vector upsert, search, and management (100% FREE, local).
"""

import logging
import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

logger = logging.getLogger("nexusai.vectorstore")


class VectorStoreService:
    """Manages vector storage and retrieval using ChromaDB (free, local)."""

    def __init__(self):
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection_name = settings.chroma_collection_name
        self._collection = None

    @property
    def collection(self):
        """Lazy-load the ChromaDB collection, creating it if necessary."""
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"📌 ChromaDB collection ready: {self.collection_name}")
        return self._collection

    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """Upsert vectors into ChromaDB in batches.

        Args:
            vectors: List of dicts with keys: id, values, metadata.
            batch_size: Number of vectors per upsert call.

        Returns:
            Total number of vectors upserted.
        """
        if not vectors:
            return 0

        total_upserted = 0

        for batch_start in range(0, len(vectors), batch_size):
            batch = vectors[batch_start : batch_start + batch_size]

            ids = [v["id"] for v in batch]
            embeddings = [v["values"] for v in batch]
            metadatas = [v.get("metadata", {}) for v in batch]

            # ChromaDB metadata values must be str, int, float, or bool
            clean_metadatas = []
            documents = []
            for m in metadatas:
                clean_m = {}
                doc_content = ""
                for k, val in m.items():
                    if k == "content":
                        doc_content = str(val)
                        clean_m[k] = str(val)[:500]  # Store truncated in metadata
                    elif isinstance(val, (str, int, float, bool)):
                        clean_m[k] = val
                    else:
                        clean_m[k] = str(val)
                clean_metadatas.append(clean_m)
                documents.append(doc_content if doc_content else " ")

            try:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=clean_metadatas,
                    documents=documents,
                )
                total_upserted += len(batch)
                logger.info(
                    f"📌 Upserted batch: {len(batch)} vectors "
                    f"(total: {total_upserted}/{len(vectors)})"
                )
            except Exception as e:
                logger.error(f"❌ Vector upsert failed at batch {batch_start}: {str(e)}")
                raise RuntimeError(f"Vector upsert failed: {str(e)}")

        logger.info(f"✅ Total vectors upserted: {total_upserted}")
        return total_upserted

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in ChromaDB.

        Args:
            query_vector: The query embedding vector.
            top_k: Maximum number of results to return.
            score_threshold: Minimum similarity score (0-1, ChromaDB uses distance).
            filter_dict: Optional metadata filter.

        Returns:
            List of results with id, score, and metadata.
        """
        try:
            query_params: Dict[str, Any] = {
                "query_embeddings": [query_vector],
                "n_results": top_k,
                "include": ["metadatas", "documents", "distances"],
            }

            if filter_dict:
                query_params["where"] = filter_dict

            response = self.collection.query(**query_params)

            results = []
            if response and response["ids"] and response["ids"][0]:
                for i, doc_id in enumerate(response["ids"][0]):
                    # ChromaDB returns cosine distance (0 = identical, 2 = opposite)
                    # Convert to similarity score: 1 - (distance / 2)
                    distance = response["distances"][0][i] if response["distances"] else 0
                    score = 1.0 - (distance / 2.0)

                    if score >= score_threshold:
                        metadata = response["metadatas"][0][i] if response["metadatas"] else {}
                        # Restore full content from documents if available
                        if response["documents"] and response["documents"][0][i]:
                            metadata["content"] = response["documents"][0][i]
                        results.append({
                            "id": doc_id,
                            "score": float(score),
                            "metadata": metadata,
                        })

            logger.info(
                f"🔍 Search returned {len(results)} results "
                f"(threshold: {score_threshold}, top_k: {top_k})"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Vector search failed: {str(e)}")
            raise RuntimeError(f"Vector search failed: {str(e)}")

    def delete_vectors(self, vector_ids: List[str]) -> None:
        """Delete vectors by their IDs.

        Args:
            vector_ids: List of vector IDs to delete.
        """
        if not vector_ids:
            return

        try:
            # ChromaDB handles batch deletion natively
            self.collection.delete(ids=vector_ids)
            logger.info(f"🗑️ Deleted {len(vector_ids)} vectors")

        except Exception as e:
            logger.error(f"❌ Vector deletion failed: {str(e)}")
            raise RuntimeError(f"Vector deletion failed: {str(e)}")

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection."""
        try:
            count = self.collection.count()
            return {
                "total_vector_count": count,
                "collection_name": self.collection_name,
                "persist_directory": settings.chroma_persist_dir,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {str(e)}")
            return {"error": str(e)}
