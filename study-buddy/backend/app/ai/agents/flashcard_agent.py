"""
Flashcard Agent — AI-Powered Study Buddy
==========================================
Extracts key terms and their definitions from study documents
and formats them as interactive flashcards.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.vector_store import VectorStoreService
from app.guardrails import validate_output
from app.prompts import FLASHCARD_PROMPT

logger = logging.getLogger("study_buddy.agents.flashcard")


class FlashcardAgent:
    """
    Flashcard Generation Agent.

    Identifies the most important terms and definitions
    in a document and structures them as flip-card pairs.
    """

    def __init__(self) -> None:
        self._vs = VectorStoreService()

    def run(
        self,
        user_id: int,
        doc_id: int,
        filename: str,
        count: int = 10,
    ) -> dict[str, Any]:
        """
        Generate flashcards from a document.

        Args:
            user_id:  Authenticated user's ID.
            doc_id:   Source document ID.
            filename: Document filename.
            count:    Number of flashcards to generate (3–30).

        Returns:
            Dict with keys: flashcards (list of {term, definition}), count, latency_ms.
        """
        start = time.perf_counter()

        chunks = self._vs.query(
            question="key terms definitions concepts vocabulary important words",
            user_id=user_id,
            doc_ids=[doc_id],
            top_k=8,
        )

        if not chunks:
            return {"flashcards": [], "count": 0, "latency_ms": 0,
                    "error": "No content found for flashcard generation."}

        context = "\n\n".join(c["content"] for c in chunks)[:6000]
        chain   = FLASHCARD_PROMPT | get_gemini_llm() | StrOutputParser()
        raw     = invoke_with_retry(chain, {"context": context, "count": count})

        cards   = _parse_flashcards(validate_output(raw))
        latency = int((time.perf_counter() - start) * 1000)

        logger.info(
            "FlashcardAgent generated %d cards for '%s' in %dms",
            len(cards), filename, latency,
        )
        return {"flashcards": cards, "count": len(cards), "latency_ms": latency}


def _parse_flashcards(raw: str) -> list[dict[str, str]]:
    """Extract and parse the JSON flashcard array from LLM output."""
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if not match:
        return []
    try:
        items = json.loads(match.group(0))
        return [
            {"term": i.get("term", "").strip(), "definition": i.get("definition", "").strip()}
            for i in items
            if i.get("term") and i.get("definition")
        ]
    except json.JSONDecodeError as e:
        logger.error("Flashcard JSON parse error: %s", e)
        return []
