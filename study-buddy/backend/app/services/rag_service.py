"""
RAG Chat Service — AI-Powered Study Buddy
==========================================
Full RAG pipeline:
  1. Validate + sanitise input (guardrails)
  2. Retrieve top-K chunks from ChromaDB
  3. Build context string
  4. Inject into RAG prompt template
  5. Invoke Gemini via LangChain chain
  6. Validate output (guardrails)
  7. Save to chat history
  8. Return answer + sources
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.vector_store import VectorStoreService
from app.core.constants import MAX_CONTEXT_CHARS
from app.guardrails import validate_input, validate_output
from app.prompts import RAG_PROMPT, TEACHING_PROMPT
from app.repositories.document_repo import DocumentRepository
from app.repositories.session_repo import SessionRepository
from app.schemas import ChatRequest, ChatResponse

logger = logging.getLogger("study_buddy.rag_service")


class RAGService:
    """Handles multi-turn RAG question answering."""

    def __init__(self, db: AsyncSession) -> None:
        self._db       = db
        self._doc_repo = DocumentRepository(db)
        self._sess_repo = SessionRepository(db)
        self._vs       = VectorStoreService()

    async def answer(
        self,
        user_id: int,
        request: ChatRequest,
        explain_level: str = "Intermediate",
        response_style: str = "clear and concise",
    ) -> ChatResponse:
        """
        Execute the RAG pipeline and return an answer.

        Args:
            user_id:        Authenticated user's ID.
            request:        ChatRequest with question and doc_ids.
            explain_level:  User preference for explanation depth.
            response_style: Verbosity preference (concise/detailed).

        Returns:
            ChatResponse with answer, sources, and latency.
        """
        start_ms = int(time.time() * 1000)

        # 1. Guardrails — validate input
        safe_question = validate_input(request.question)

        # 2. Retrieve relevant chunks
        chunks = self._vs.query(
            question=safe_question,
            user_id=user_id,
            doc_ids=request.document_ids,
        )

        if not chunks:
            answer = (
                "I couldn't find relevant information in your documents. "
                "Please check that the document was uploaded and indexed successfully, "
                "or try rephrasing your question."
            )
            sources: list[str] = []
        else:
            # 3. Build context (cap at MAX_CONTEXT_CHARS)
            context = _build_context(chunks)

            # 4. Retrieve recent chat history for memory
            recent = await self._sess_repo.recent_chats(user_id, limit=5)
            history_str = "\n".join(
                f"Q: {c.question}\nA: {c.answer[:200]}" for c in reversed(recent)
            ) or "No previous conversation."

            # 5. Build LangChain chain
            llm   = get_gemini_llm()
            chain = RAG_PROMPT | llm | StrOutputParser()

            # 6. Invoke Gemini
            raw_answer = invoke_with_retry(
                chain,
                {
                    "question":       safe_question,
                    "context":        context,
                    "chat_history":   history_str,
                    "explain_level":  explain_level,
                    "response_style": response_style,
                },
            )

            # 7. Validate output
            answer  = validate_output(raw_answer)
            sources = list({c["filename"] for c in chunks})

        # 8. Save to history
        doc_id = request.document_ids[0] if request.document_ids else None
        await self._sess_repo.save_chat(
            user_id=user_id,
            document_id=doc_id,
            question=safe_question,
            answer=answer,
            sources=str(sources),
            intent="ask",
        )

        latency = int(time.time() * 1000) - start_ms
        logger.info("RAG answered in %dms for user_id=%d", latency, user_id)

        return ChatResponse(
            answer=answer,
            sources=sources,
            intent="ask",
            latency_ms=latency,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_context(chunks: list[dict[str, Any]]) -> str:
    """Concatenate retrieved chunks into a context string."""
    parts: list[str] = []
    total = 0
    for chunk in chunks:
        text = f"[Source: {chunk['filename']}]\n{chunk['content']}"
        if total + len(text) > MAX_CONTEXT_CHARS:
            break
        parts.append(text)
        total += len(text)
    return "\n\n---\n\n".join(parts)
