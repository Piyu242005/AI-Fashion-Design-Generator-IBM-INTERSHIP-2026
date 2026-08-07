"""
Vector Store Service — AI-Powered Study Buddy
===============================================
ChromaDB wrapper for storing and querying document embeddings.
Uses Sentence Transformers (all-MiniLM-L6-v2) as the embedding function.
Singleton pattern — one collection, shared across requests.
"""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.config import settings
from app.utils.text_splitter import TextChunk

logger = logging.getLogger("study_buddy.vector_store")


class VectorStoreService:
    """ChromaDB wrapper. Instantiate per-request; collection is a singleton."""

    def __init__(self) -> None:
        self._client     = _get_chroma_client()
        self._embed_fn   = _get_embedding_function()
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.debug("VectorStore ready — collection: %s", settings.CHROMA_COLLECTION_NAME)

    async def add_chunks(
        self,
        chunks: list[TextChunk],
        doc_id: int,
        user_id: int,
        filename: str,
    ) -> list[str]:
        """
        Embed and store chunks in ChromaDB.

        Returns:
            List of ChromaDB IDs assigned to the chunks.
        """
        ids       = [str(uuid.uuid4()) for _ in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "doc_id":      str(doc_id),
                "user_id":     str(user_id),
                "filename":    filename,
                "chunk_index": str(c.chunk_index),
                "char_start":  str(c.char_start),
            }
            for c in chunks
        ]

        # ChromaDB add is sync — run in thread pool for async compat
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            ),
        )

        logger.info("Stored %d chunks for doc_id=%d", len(chunks), doc_id)
        return ids

    def query(
        self,
        question: str,
        user_id: int,
        doc_ids: list[int],
        top_k: int | None = None,
        distance_threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a question.

        Chunks with cosine distance > distance_threshold are filtered out —
        they are semantically too far from the query and would hurt answer
        quality (hallucination risk).

        Args:
            question:           User query string.
            user_id:            Restricts results to this user's documents.
            doc_ids:            Further restrict to these specific document IDs.
            top_k:              Number of results (defaults to settings.RAG_TOP_K).
            distance_threshold: Drop chunks with cosine distance above this value.
                                0.0 = perfect match only; 1.0 = keep everything.
                                Default 0.8 gives a good relevance/recall tradeoff.

        Returns:
            List of dicts with 'content', 'filename', 'doc_id', 'distance',
            sorted by ascending distance (most relevant first).
        """
        k = top_k or settings.RAG_TOP_K

        where_filter: dict[str, Any] = {
            "$and": [
                {"user_id": {"$eq": str(user_id)}},
                {"doc_id":  {"$in": [str(d) for d in doc_ids]}},
            ]
        }

        results = self._collection.query(
            query_texts=[question],
            n_results=min(k, self._collection.count() or 1),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                # Filter out chunks that are semantically too distant
                if dist > distance_threshold:
                    logger.debug(
                        "Dropped chunk with distance=%.4f > threshold=%.2f for user_id=%d",
                        dist, distance_threshold, user_id,
                    )
                    continue
                chunks.append({
                    "content":  doc,
                    "filename": meta.get("filename", ""),
                    "doc_id":   meta.get("doc_id", ""),
                    "distance": round(dist, 4),
                })

        logger.debug(
            "Query returned %d/%d chunks (threshold=%.2f) for user_id=%d",
            len(chunks), k, distance_threshold, user_id,
        )
        return chunks

    def delete_chunks(self, chroma_ids: list[str]) -> None:
        """Delete specific chunks by their ChromaDB IDs."""
        if chroma_ids:
            self._collection.delete(ids=chroma_ids)
            logger.info("Deleted %d chunks from ChromaDB", len(chroma_ids))


# ---------------------------------------------------------------------------
# Singletons (one client + one embedding function per process)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(settings.chroma_path))


@lru_cache(maxsize=1)
def _get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    return SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )
