"""
Summary Agent — AI-Powered Study Buddy
=========================================
Generates concise, structured summaries of study documents.
Supports bullet-point and paragraph styles with three detail levels.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.memory_manager import get_user_preferences
from app.ai.vector_store import VectorStoreService
from app.guardrails import validate_output
from app.prompts import SUMMARY_BULLET_PROMPT, SUMMARY_PARAGRAPH_PROMPT

logger = logging.getLogger("study_buddy.agents.summary")

_DETAIL_MAP = {
    "brief":    "brief (3-5 key points only)",
    "standard": "standard (5-8 key points, covering main themes)",
    "detailed": "detailed (8-12 points, covering all important concepts)",
}

_PROMPT_MAP = {
    "bullet":    SUMMARY_BULLET_PROMPT,
    "paragraph": SUMMARY_PARAGRAPH_PROMPT,
}


class SummaryAgent:
    """
    Document Summarisation Agent.

    Retrieves a broad sample of chunks from ChromaDB,
    assembles a representative context, and generates a
    structured summary via Gemini.
    """

    def __init__(self) -> None:
        self._vs = VectorStoreService()

    def run(
        self,
        user_id: int,
        doc_id: int,
        filename: str,
        style: str = "bullet",
        detail: str = "standard",
        override_prefs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a document summary.

        Args:
            user_id:  Authenticated user's ID.
            doc_id:   Document to summarise.
            filename: Document filename for logging.
            style:    'bullet' or 'paragraph'.
            detail:   'brief' | 'standard' | 'detailed'.

        Returns:
            Dict with keys: summary, style, detail, latency_ms.
        """
        start = time.perf_counter()

        # Broad retrieval for full-document coverage
        chunks = self._vs.query(
            question="overview main concepts key ideas important topics",
            user_id=user_id,
            doc_ids=[doc_id],
            top_k=10,
        )

        if not chunks:
            return {
                "summary":    "No content could be retrieved from this document.",
                "style":      style,
                "detail":     detail,
                "latency_ms": 0,
            }

        context    = "\n\n".join(c["content"] for c in chunks)[:7000]
        detail_str = _DETAIL_MAP.get(detail, _DETAIL_MAP["standard"])
        prompt     = _PROMPT_MAP.get(style, SUMMARY_BULLET_PROMPT)
        chain      = prompt | get_gemini_llm() | StrOutputParser()

        raw     = invoke_with_retry(chain, {"context": context, "detail": detail_str})
        summary = validate_output(raw)

        latency = int((time.perf_counter() - start) * 1000)
        logger.info("SummaryAgent completed '%s' in %dms", filename, latency)

        return {
            "summary":    summary,
            "style":      style,
            "detail":     detail,
            "latency_ms": latency,
        }
