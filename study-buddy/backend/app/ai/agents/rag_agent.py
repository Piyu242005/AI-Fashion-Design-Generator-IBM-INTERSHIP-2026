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

        # ── 8. Grounding evaluation (lightweight, no extra LLM call) ──────
        grounding = _evaluate_grounding(answer, context)
        if not grounding["is_grounded"]:
            logger.warning(
                "RAGAgent grounding check FAILED for user_id=%d: "
                "answer may not be supported by retrieved context. "
                "overlap_ratio=%.2f overlap_words=%d",
                user_id,
                grounding["overlap_ratio"],
                grounding["overlap_words"],
            )

        # ── 9. Update session memory ───────────────────────────────────────
        save_to_session_memory(user_id, question, answer)

        latency = int((time.perf_counter() - start) * 1000)
        logger.info(
            "RAGAgent answered in %dms, %d chunks used, grounded=%s",
            latency, len(chunks_sorted), grounding["is_grounded"],
        )

        return {
            "answer":         answer,
            "sources":        sources,
            "chunks_used":    len(chunks_sorted),
            "latency_ms":     latency,
            "is_grounded":    grounding["is_grounded"],
            "grounding_score": grounding["overlap_ratio"],
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


def _evaluate_grounding(answer: str, context: str) -> dict:
    """
    Lightweight grounding check — measures lexical overlap between the
    generated answer and the retrieved context.

    This is a fast, zero-cost heuristic (no extra LLM call) that catches
    obvious hallucinations where the answer shares no vocabulary with the
    source material.

    Approach:
      - Tokenise both texts into lowercase word sets (stop words excluded).
      - Compute overlap ratio = |answer_words ∩ context_words| / |answer_words|
      - Flag as ungrounded if overlap ratio < 0.15 (15%) and answer is long.

    Production upgrade: Replace with RAGAS faithfulness metric for proper
    semantic grounding evaluation.

    Returns:
        Dict with is_grounded (bool), overlap_ratio (float), overlap_words (int).
    """
    # Minimal stop-word set — common English words that carry no signal
    _STOP = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
        "that", "this", "it", "its", "from", "by", "as", "not", "can", "will",
        "your", "you", "i", "we", "they", "he", "she", "my", "our", "their",
    }

    def _tokenise(text: str) -> set[str]:
        import re
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        return {w for w in words if w not in _STOP}

    answer_words  = _tokenise(answer)
    context_words = _tokenise(context)

    if not answer_words:
        return {"is_grounded": True, "overlap_ratio": 1.0, "overlap_words": 0}

    overlap       = answer_words & context_words
    overlap_ratio = len(overlap) / len(answer_words)
    # Only flag short answers (< 50 words) as suspicious if ratio is very low
    min_ratio     = 0.10 if len(answer_words) < 50 else 0.15
    is_grounded   = overlap_ratio >= min_ratio

    return {
        "is_grounded":   is_grounded,
        "overlap_ratio": round(overlap_ratio, 4),
        "overlap_words": len(overlap),
    }
