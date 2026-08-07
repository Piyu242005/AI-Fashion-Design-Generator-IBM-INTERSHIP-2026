"""
Document Repository — AI-Powered Study Buddy
=============================================
Data access layer for Document model.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        user_id: int,
        filename: str,
        file_type: str,
        file_path: str,
        file_size_kb: int,
    ) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            file_size_kb=file_size_kb,
            status="processing",
        )
        self._db.add(doc)
        await self._db.commit()
        await self._db.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: int) -> Document | None:
        result = await self._db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Document]:
        result = await self._db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def update_after_index(
        self,
        doc: Document,
        chunk_count: int,
        chroma_ids: str,
        status: str = "ready",
    ) -> Document:
        doc.chunk_count = chunk_count
        doc.chroma_ids  = chroma_ids
        doc.status      = status
        await self._db.commit()
        await self._db.refresh(doc)
        return doc

    async def delete(self, doc: Document) -> None:
        await self._db.delete(doc)
        await self._db.commit()
