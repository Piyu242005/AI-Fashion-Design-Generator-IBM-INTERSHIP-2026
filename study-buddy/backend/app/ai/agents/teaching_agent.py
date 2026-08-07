"""
Teaching Agent — AI-Powered Study Buddy
=========================================
Explains concepts in plain, student-friendly language.
Uses analogies, real-world examples, and step-by-step breakdowns.
Adapts explanation depth to the user's configured explanation level.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.memory_manager import get_user_preferences, save_to_session_memory
from app.ai.vector_store import VectorStoreService
from app.guardrails import validate_output
from app.prompts import TEACHING_PROMPT

logger = logging.getLogger("study_buddy.agents.teaching")

_LEVEL_MAP = {
    "Beginner (ELI5)": "beginner (explain like I'm 10, use very simple words and relatable analogies)",
    "Intermediate":    "intermediate (use standard academic language with examples)",
    "Advanced":        "advanced (use technical terminology and in-depth analysis)",
}


class TeachingAgent:
    """
    Concept Explanation Agent.

    Retrieves relevant document context and uses Gemini to
    explain concepts clearly with analogies and examples,
    adapted to the student's expertise level.
    """

    def __init__(self) -> None:
        self._vs = VectorStoreService()

    def run(
        self,
        user_id: int,
        concept: str,
        doc_ids: list[int],
        override_prefs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Explain a concept using document context.

        Args:
            user_id:  Authenticated user's ID.
            concept:  The concept or topic to explain.
            doc_ids:  Documents to retrieve context from.

        Returns:
            Dict with keys: explanation, sources, latency_ms.
        """
        start = time.perf_counter()
        prefs = {**get_user_preferences(user_id), **(override_prefs or {})}
        level = _LEVEL_MAP.get(
            prefs.get("explain_level", "Intermediate"),
            _LEVEL_MAP["Intermediate"],
        )

        # Retrieve relevant context
        chunks = self._vs.query(
            question=concept,
            user_id=user_id,
            doc_ids=doc_ids,
            top_k=5,
        )

        context = (
            "\n\n".join(c["content"] for c in chunks)[:5000]
            if chunks
            else "No specific document context available — use your general knowledge."
        )
        sources = list({c["filename"] for c in chunks}) if chunks else []

        chain  = TEACHING_PROMPT | get_gemini_llm() | StrOutputParser()
        raw    = invoke_with_retry(chain, {
            "context":       context,
            "question":      concept,
            "explain_level": level,
        })

        explanation = validate_output(raw)
        save_to_session_memory(user_id, concept, explanation)

        latency = int((time.perf_counter() - start) * 1000)
        logger.info("TeachingAgent explained '%s' in %dms", concept[:50], latency)

        return {
            "explanation": explanation,
            "sources":     sources,
            "latency_ms":  latency,
        }
