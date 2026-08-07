"""
Flashcard Service — AI-Powered Study Buddy
============================================
Generates term→definition flashcards from uploaded documents.
"""

from __future__ import annotations

import json
import logging
import re

from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.vector_store import VectorStoreService
from app.exceptions import NotFoundError
from app.guardrails import validate_output
from app.prompts import FLASHCARD_PROMPT
from app.repositories.document_repo import DocumentRepository
from app.schemas import Flashcard, FlashcardRequest, FlashcardsResponse

logger = logging.getLogger("study_buddy.flashcard_service")


class FlashcardService:
    def __init__(self, db: AsyncSession) -> None:
        self._doc_repo = DocumentRepository(db)
        self._vs       = VectorStoreService()

    async def generate(self, user_id: int, req: FlashcardRequest) -> FlashcardsResponse:
        """Generate flashcards from a document."""
        doc = await self._doc_repo.get_by_id(req.document_id)
        if not doc or doc.user_id != user_id:
            raise NotFoundError("Document")

        chunks = self._vs.query(
            question="key terms definitions concepts vocabulary",
            user_id=user_id,
            doc_ids=[req.document_id],
            top_k=8,
        )
        if not chunks:
            raise ValueError("No content found in document for flashcard generation.")

        context = "\n\n".join(c["content"] for c in chunks)[:6000]
        llm     = get_gemini_llm()
        chain   = FLASHCARD_PROMPT | llm | StrOutputParser()

        raw       = invoke_with_retry(chain, {"context": context, "count": req.count})
        validated = validate_output(raw)
        cards     = _parse_flashcards(validated)

        logger.info(
            "Generated %d flashcards for doc_id=%d user_id=%d",
            len(cards), req.document_id, user_id,
        )
        return FlashcardsResponse(
            document_id=req.document_id,
            flashcards=cards,
            count=len(cards),
        )


def _parse_flashcards(raw: str) -> list[Flashcard]:
    """Parse JSON array of {term, definition} from LLM output."""
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if not match:
        return []
    try:
        items = json.loads(match.group(0))
        return [
            Flashcard(
                term=item.get("term", "").strip(),
                definition=item.get("definition", "").strip(),
            )
            for item in items
            if item.get("term") and item.get("definition")
        ]
    except json.JSONDecodeError as e:
        logger.error("JSON parse error in flashcard response: %s", e)
        return []
