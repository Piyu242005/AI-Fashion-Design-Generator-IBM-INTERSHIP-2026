"""
Document Service — AI-Powered Study Buddy
==========================================
Orchestrates the full document ingestion pipeline:
  1. Validate file
  2. Save to disk
  3. Extract text
  4. Split into chunks
  5. Embed chunks
  6. Store in ChromaDB
  7. Update DB record
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import NotFoundError, ForbiddenError
from app.repositories.document_repo import DocumentRepository
from app.schemas import DocumentOut, DocumentUploadResponse
from app.utils.file_validator import validate_upload
from app.utils.text_extractor import extract_text
from app.utils.text_splitter import split_text

logger = logging.getLogger("study_buddy.doc_service")


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = DocumentRepository(db)

    async def upload_and_index(
        self,
        user_id: int,
        file_bytes: bytes,
        filename: str,
    ) -> DocumentUploadResponse:
        """
        Full ingestion pipeline for an uploaded file.

        Returns:
            DocumentUploadResponse with chunk count and status.
        """
        # 1. Validate
        ext = validate_upload(file_bytes, filename)

        # 2. Save to disk with a unique name to avoid collisions
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path   = settings.upload_path / unique_name
        file_path.write_bytes(file_bytes)
        size_kb = len(file_bytes) // 1024

        # 3. Create DB record (status=processing)
        doc = await self._repo.create(
            user_id=user_id,
            filename=filename,
            file_type=ext,
            file_path=str(file_path),
            file_size_kb=size_kb,
        )

        try:
            # 4. Extract text
            raw_text = extract_text(file_path)

            # 5. Split into chunks
            chunks = split_text(raw_text, source=filename)

            if not chunks:
                raise RuntimeError("No text could be extracted from this file.")

            # 6. Embed and store in ChromaDB
            from app.ai.vector_store import VectorStoreService
            vs = VectorStoreService()
            chroma_ids = await vs.add_chunks(
                chunks=chunks,
                doc_id=doc.id,
                user_id=user_id,
                filename=filename,
            )

            # 7. Update DB record
            doc = await self._repo.update_after_index(
                doc=doc,
                chunk_count=len(chunks),
                chroma_ids=json.dumps(chroma_ids),
                status="ready",
            )

            logger.info(
                "Indexed doc id=%d '%s' — %d chunks", doc.id, filename, len(chunks)
            )
            return DocumentUploadResponse(
                id=doc.id,
                filename=doc.filename,
                chunk_count=doc.chunk_count,
                status=doc.status,
                message=f"Successfully indexed {len(chunks)} chunks.",
            )

        except Exception as exc:
            # Mark document as error state
            await self._repo.update_after_index(doc, 0, "[]", status="error")
            logger.error("Indexing failed for doc id=%d: %s", doc.id, exc)
            raise RuntimeError(str(exc)) from exc

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
