"""
Quiz Agent — AI-Powered Study Buddy
======================================
Generates high-quality quizzes from document content.
Supports MCQ, True/False, Short Answer, and Mixed modes.
Applies difficulty instructions from QUIZ_DIFFICULTY_MAP.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.memory_manager import get_user_preferences
from app.ai.vector_store import VectorStoreService
from app.core.constants import QUIZ_DIFFICULTY_MAP
from app.guardrails import validate_output
from app.prompts import QUIZ_MCQ_PROMPT, QUIZ_SA_PROMPT, QUIZ_TF_PROMPT

logger = logging.getLogger("study_buddy.agents.quiz")

_PROMPT_MAP = {
    "mcq":          QUIZ_MCQ_PROMPT,
    "true_false":   QUIZ_TF_PROMPT,
    "short_answer": QUIZ_SA_PROMPT,
}


class QuizAgent:
    """
    Quiz Generation Agent.

    Selects appropriate prompt, retrieves document context,
    invokes Gemini, and parses the JSON quiz response.
    """

    def __init__(self) -> None:
        self._vs = VectorStoreService()

    def run(
        self,
        user_id: int,
        doc_id: int,
        filename: str,
        question_type: str = "mcq",
        num_questions: int = 5,
        difficulty: str = "medium",
        topic: str | None = None,
        override_prefs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Generate quiz questions for a document.

        Returns:
            Dict with keys: questions (list), num_questions, latency_ms.
        """
        start = time.perf_counter()
        prefs = {**get_user_preferences(user_id), **(override_prefs or {})}

        # Apply user difficulty preference if not explicitly overridden
        effective_diff = difficulty or prefs.get("quiz_diff", "Medium").lower()
        diff_instruction = QUIZ_DIFFICULTY_MAP.get(
            effective_diff, QUIZ_DIFFICULTY_MAP["medium"]
        )

        # Query for broad coverage of the document
        query = topic or f"main topics and key concepts in {filename}"
        chunks = self._vs.query(
            question=query,
            user_id=user_id,
            doc_ids=[doc_id],
            top_k=8,
        )

        if not chunks:
            return {"questions": [], "num_questions": 0, "latency_ms": 0,
                    "error": "No document content found for quiz generation."}

        context = "\n\n".join(c["content"] for c in chunks)[:6000]

        # Handle mixed type
        if question_type == "mixed":
            half = num_questions // 2
            rest = num_questions - half
            mcq  = self._gen_type(context, "mcq",        half, diff_instruction)
            tf   = self._gen_type(context, "true_false",  rest, diff_instruction)
            questions = mcq + tf
        else:
            questions = self._gen_type(context, question_type, num_questions, diff_instruction)

        latency = int((time.perf_counter() - start) * 1000)
        logger.info(
            "QuizAgent generated %d questions (%s, %s) in %dms",
            len(questions), question_type, effective_diff, latency,
        )
        return {
            "questions":     questions,
            "num_questions": len(questions),
            "question_type": question_type,
            "difficulty":    effective_diff,
            "latency_ms":    latency,
        }

    def _gen_type(
        self,
        context: str,
        qtype: str,
        count: int,
        difficulty: str,
    ) -> list[dict[str, Any]]:
        prompt = _PROMPT_MAP.get(qtype, QUIZ_MCQ_PROMPT)
        chain  = prompt | get_gemini_llm() | StrOutputParser()
        raw    = invoke_with_retry(chain, {
            "context":       context,
            "num_questions": count,
            "difficulty":    difficulty,
        })
        return _parse_json_questions(validate_output(raw), qtype)


def _parse_json_questions(raw: str, qtype: str) -> list[dict[str, Any]]:
    """Safely parse JSON array from LLM output."""
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if not match:
        logger.warning("No JSON array in quiz response")
        return []
    try:
        items = json.loads(match.group(0))
        return [
            {
                "question":    item.get("question", ""),
                "options":     item.get("options", []),
                "answer":      item.get("answer", ""),
                "explanation": item.get("explanation", ""),
                "type":        item.get("type", qtype),
            }
            for item in items
            if item.get("question") and item.get("answer")
        ]
    except json.JSONDecodeError as e:
        logger.error("Quiz JSON parse error: %s", e)
        return []
