"""
RAG Agent — AI-Powered Study Buddy
=====================================
Handles document-grounded Q&A using Retrieval-Augmented Generation.

Pipeline:
  1. Embed user question
  2. Retrieve top-K chunks from ChromaDB
  3. Rerank by relevance score
  4. Build structured context
  5. Inject into RAG prompt with session memory
  6. Invoke Gemini
  7. Validate output
  8. Persist to chat history

Supports conversation memory — references previous turns for
multi-turn study sessions.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.memory_manager import (
    get_user_preferences,
    save_to_session_memory,
    get_session_history_str,
)
from app.ai.vector_store import VectorStoreService
from app.core.constants import MAX_CONTEXT_CHARS
from app.guardrails import validate_input, validate_output
from app.prompts import RAG_PROMPT

logger = logging.getLogger("study_buddy.agents.rag")


class RAGAgent:
    """
    RAG Question-Answering Agent.

    Retrieves relevant document chunks and uses Gemini to produce
    accurate, grounded answers with source citations.
    """

    def __init__(self) -> None:
        self._vs = VectorStoreService()

    def run(
        self,
        user_id: int,
        question: str,
        doc_ids: list[int],
        override_prefs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the RAG pipeline.

        Args:
            user_id:        Authenticated user's ID.
            question:       Validated user question.
            doc_ids:        List of document IDs to query.
            override_prefs: Optional preference overrides (style, level).

        Returns:
            Dict with keys: answer, sources, chunks_used, latency_ms.
        """
        start = time.perf_counter()
        prefs = {**get_user_preferences(user_id), **(override_prefs or {})}

        # ── 1. Retrieve chunks ─────────────────────────────────────────────
        chunks = self._vs.query(
            question=question,
            user_id=user_id,
            doc_ids=doc_ids,
        )

        if not chunks:
            return {
                "answer": (
                    "I couldn't find relevant information in your uploaded documents.\n\n"
                    "**Suggestions:**\n"
                    "• Make sure the document was uploaded and indexed successfully.\n"
                    "• Try rephrasing your question.\n"
                    "• Check the Document page to confirm the document status is 'ready'."
                ),
                "sources":      [],
                "chunks_used":  0,
                "latency_ms":   int((time.perf_counter() - start) * 1000),
            }

        # ── 2. Rerank — sort by ascending distance (most similar first) ────
        chunks_sorted = sorted(chunks, key=lambda c: c["distance"])

        # ── 3. Build context (cap at MAX_CONTEXT_CHARS) ────────────────────
        context = _build_context(chunks_sorted)

        # ── 4. Session memory ──────────────────────────────────────────────
        history_str = get_session_history_str(user_id)

        # ── 5. Map preferences to prompt vars ─────────────────────────────
        style_map   = {"Concise": "brief and to the point",
                       "Standard": "clear and educational",
                       "Detailed": "thorough and comprehensive"}
        explain_map = {"Beginner (ELI5)": "beginner (use simple words and analogies)",
                       "Intermediate": "intermediate",
                       "Advanced": "advanced"}

        response_style = style_map.get(prefs.get("ai_style", "Standard"), "clear and educational")
        explain_level  = explain_map.get(prefs.get("explain_level", "Intermediate"), "intermediate")

        # ── 6. Build and invoke chain ──────────────────────────────────────
        chain = RAG_PROMPT | get_gemini_llm() | StrOutputParser()
        raw   = invoke_with_retry(chain, {
            "question":       question,
            "context":        context,
            "chat_history":   history_str,
            "response_style": response_style,
            "explain_level":  explain_level,
        })

        # ── 7. Validate output ─────────────────────────────────────────────
        answer  = validate_output(raw)
        sources = list({c["filename"] for c in chunks_sorted})

        # ── 8. Update session memory ───────────────────────────────────────
        save_to_session_memory(user_id, question, answer)

        latency = int((time.perf_counter() - start) * 1000)
        logger.info("RAGAgent answered in %dms, %d chunks used", latency, len(chunks_sorted))

        return {
            "answer":      answer,
            "sources":     sources,
            "chunks_used": len(chunks_sorted),
            "latency_ms":  latency,
        }


def _build_context(chunks: list[dict[str, Any]]) -> str:
    """Concatenate chunks into a numbered context block."""
    parts: list[str] = []
    total = 0
    for i, chunk in enumerate(chunks, 1):
        text = f"[{i}. Source: {chunk['filename']}]\n{chunk['content']}"
        if total + len(text) > MAX_CONTEXT_CHARS:
            break
        parts.append(text)
        total += len(text)
    return "\n\n---\n\n".join(parts)
