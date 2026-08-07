"""
Summary Service — AI-Powered Study Buddy
==========================================
Generates bullet or paragraph summaries of uploaded documents.
"""

from __future__ import annotations

import logging

from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import async_invoke_with_retry, get_gemini_llm
from app.ai.vector_store import VectorStoreService
from app.exceptions import NotFoundError
from app.guardrails import validate_output
from app.prompts import SUMMARY_BULLET_PROMPT, SUMMARY_PARAGRAPH_PROMPT
from app.repositories.document_repo import DocumentRepository
from app.schemas import SummaryRequest, SummaryResponse

logger = logging.getLogger("study_buddy.summary_service")

_DETAIL_MAP = {
    "brief":    "brief (3-5 key points)",
    "standard": "standard (5-8 key points)",
    "detailed": "detailed (8-12 key points)",
}


class SummaryService:
    def __init__(self, db: AsyncSession) -> None:
        self._doc_repo = DocumentRepository(db)
        self._vs       = VectorStoreService()

    async def summarise(self, user_id: int, req: SummaryRequest) -> SummaryResponse:
        """Generate a summary for a document."""
        doc = await self._doc_repo.get_by_id(req.document_id)
        if not doc or doc.user_id != user_id:
            raise NotFoundError("Document")

        # Retrieve a broad set of chunks (top 10) for full-document coverage
        chunks = self._vs.query(
            question="overview key concepts main topics summary",
            user_id=user_id,
            doc_ids=[req.document_id],
            top_k=10,
        )
        if not chunks:
            raise ValueError("No content found in document for summarisation.")

        context   = "\n\n".join(c["content"] for c in chunks)[:7000]
        detail_str = _DETAIL_MAP.get(req.detail, _DETAIL_MAP["standard"])

        prompt = SUMMARY_BULLET_PROMPT if req.style == "bullet" else SUMMARY_PARAGRAPH_PROMPT
        llm    = get_gemini_llm()
        chain  = prompt | llm | StrOutputParser()

        raw     = await async_invoke_with_retry(chain, {"context": context, "detail": detail_str})
        summary = validate_output(raw)

        logger.info("Summary generated for doc_id=%d user_id=%d", req.document_id, user_id)
        return SummaryResponse(
            document_id=req.document_id,
            filename=doc.filename,
            summary=summary,
            style=req.style,
        )
