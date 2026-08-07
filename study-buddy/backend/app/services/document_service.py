"""
Document Service — AI-Powered Study Buddy
==========================================
Orchestrates the document ingestion pipeline in two phases:

  Phase 1 — accept_upload() (fast, in-request, < 100 ms):
    1. Validate file type + size
    2. Save file bytes to disk
    3. Create DB record with status="processing"
    4. Return DocumentUploadResponse immediately (202 Accepted)

  Phase 2 — index_document() (slow, in BackgroundTask, 2-30 seconds):
    5. Extract text from file
    6. Split into chunks
    7. Embed chunks via SentenceTransformers
    8. Store in ChromaDB
    9. Update DB record to status="ready"

This design keeps the HTTP response fast regardless of file size.
Use GET /documents/{id}/status to poll when indexing is complete.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.exceptions import ForbiddenError, NotFoundError
from app.repositories.document_repo import DocumentRepository
from app.schemas import DocumentOut, DocumentUploadResponse
from app.utils.file_validator import validate_upload
from app.utils.text_extractor import extract_text
from app.utils.text_splitter import split_text

logger = logging.getLogger("study_buddy.doc_service")


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self._db   = db
        self._repo = DocumentRepository(db)

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 1 — Fast path (called in-request, returns 202 immediately)
    # ──────────────────────────────────────────────────────────────────────────

    async def accept_upload(
        self,
        user_id: int,
        file_bytes: bytes,
        filename: str,
    ) -> DocumentUploadResponse:
        """
        Validate, save, and register the file.  Returns immediately.
        Heavy indexing is delegated to index_document() as a BackgroundTask.
        """
        # 1. Validate file type and size (raises on failure)
        ext = validate_upload(file_bytes, filename)

        # 2. Save to disk with a UUID prefix to avoid collisions
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path   = settings.upload_path / unique_name
        file_path.write_bytes(file_bytes)
        size_kb = len(file_bytes) // 1024

        # 3. Create DB record with status="processing"
        doc = await self._repo.create(
            user_id=user_id,
            filename=filename,
            file_type=ext,
            file_path=str(file_path),
            file_size_kb=size_kb,
        )

        logger.info(
            "Accepted upload doc_id=%d '%s' (%d KB) — queued for indexing",
            doc.id, filename, size_kb,
        )
        return DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            chunk_count=0,
            status="processing",
            message="File accepted. Indexing in progress — poll /status for updates.",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 2 — Heavy path (called as BackgroundTask, after response is sent)
    # ──────────────────────────────────────────────────────────────────────────

    async def index_document(self, doc_id: int, user_id: int) -> None:
        """
        Extract, chunk, embed, and store a document in ChromaDB.

        Opens its own DB session because the request session is already closed
        when BackgroundTasks run.
        """
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            doc  = await repo.get_by_id(doc_id)
            if not doc:
                logger.error("index_document: doc_id=%d not found", doc_id)
                return

            try:
                # 4. Extract text
                raw_text = extract_text(Path(doc.file_path))

                # 5. Split into chunks
                chunks = split_text(raw_text, source=doc.filename)
                if not chunks:
                    raise RuntimeError("No text could be extracted from this file.")

                # 6. Embed and store in ChromaDB
                from app.ai.vector_store import VectorStoreService
                vs = VectorStoreService()
                chroma_ids = await vs.add_chunks(
                    chunks=chunks,
                    doc_id=doc.id,
                    user_id=user_id,
                    filename=doc.filename,
                )

                # 7. Update DB record to ready
                await repo.update_after_index(
                    doc=doc,
                    chunk_count=len(chunks),
                    chroma_ids=json.dumps(chroma_ids),
                    status="ready",
                )
                logger.info(
                    "Indexed doc_id=%d '%s' — %d chunks",
                    doc.id, doc.filename, len(chunks),
                )

            except Exception as exc:
                await repo.update_after_index(doc, 0, "[]", status="error")
                logger.error("Indexing failed for doc_id=%d: %s", doc_id, exc)

    # ──────────────────────────────────────────────────────────────────────────
    # Status polling endpoint helper
    # ──────────────────────────────────────────────────────────────────────────

    async def get_status(self, user_id: int, doc_id: int) -> dict:
        """Return current indexing status for a document."""
        doc = await self._repo.get_by_id(doc_id)
        if not doc or doc.user_id != user_id:
            raise NotFoundError("Document")
        return {
            "id":          doc.id,
            "filename":    doc.filename,
            "status":      doc.status,
            "chunk_count": doc.chunk_count,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Backward-compatible wrapper (used by tests that expect the old interface)
    # ──────────────────────────────────────────────────────────────────────────

    async def upload_and_index(
        self,
        user_id: int,
        file_bytes: bytes,
        filename: str,
    ) -> DocumentUploadResponse:
        """
        Synchronous-style full pipeline (kept for test compatibility).
        Runs accept_upload then index_document in sequence.
        """
        pending = await self.accept_upload(user_id, file_bytes, filename)
        await self.index_document(pending.id, user_id)
        # Re-fetch to return final state
        doc = await self._repo.get_by_id(pending.id)
        if doc:
            return DocumentUploadResponse(
                id=doc.id,
                filename=doc.filename,
                chunk_count=doc.chunk_count,
                status=doc.status,
                message=f"Indexed {doc.chunk_count} chunks.",
            )
        return pending

    async def list_documents(self, user_id: int) -> list[DocumentOut]:
        docs = await self._repo.list_by_user(user_id)
        return [DocumentOut.model_validate(d) for d in docs]

    async def delete_document(self, user_id: int, doc_id: int) -> None:
        doc = await self._repo.get_by_id(doc_id)
        if not doc:
            raise NotFoundError("Document")
        if doc.user_id != user_id:
            raise ForbiddenError()

        # Remove from ChromaDB
        try:
            from app.ai.vector_store import VectorStoreService
            vs = VectorStoreService()
            chroma_ids = json.loads(doc.chroma_ids or "[]")
            if chroma_ids:
                vs.delete_chunks(chroma_ids)
        except Exception as e:
            logger.warning("ChromaDB delete failed for doc %d: %s", doc_id, e)

        # Delete file from disk
        try:
            Path(doc.file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning("Disk delete failed for doc %d: %s", doc_id, e)

        await self._repo.delete(doc)
        logger.info("Deleted doc id=%d user_id=%d", doc_id, user_id)
