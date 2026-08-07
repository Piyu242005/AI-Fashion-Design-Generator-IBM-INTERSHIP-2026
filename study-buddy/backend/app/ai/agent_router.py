"""
Agent Router — AI-Powered Study Buddy
========================================
The central intelligent dispatcher. Classifies the user's intent
and routes the request to the appropriate specialised agent.

Architecture:
  User Message
       │
       ▼
  IntentClassifier (keyword + pattern matching)
       │
       ├── "ask"       → RAGAgent
       ├── "quiz"      → QuizAgent
       ├── "summary"   → SummaryAgent
       ├── "flashcard" → FlashcardAgent
       └── "teach"     → TeachingAgent
             │
             ▼
      AI Guardrails Layer
             │
             ▼
      Gemini 1.5 Pro
             │
             ▼
      Validated Response → User

This design follows the Multi-Agent Orchestration pattern and
makes each agent independently testable and replaceable.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.ai.agents import (
    FlashcardAgent,
    QuizAgent,
    RAGAgent,
    SummaryAgent,
    TeachingAgent,
)
from app.ai.intent_classifier import classify_intent, get_intent_description
from app.guardrails import validate_input

logger = logging.getLogger("study_buddy.agent_router")


class AgentRouter:
    """
    Central AI dispatcher — routes requests to specialised agents.

    Usage:
        router = AgentRouter()
        result = router.route(
            user_id=1,
            message="Summarise my notes on photosynthesis",
            doc_ids=[3],
            doc_id=3,
            filename="biology_notes.pdf",
        )
    """

    def __init__(self) -> None:
        # Agents are instantiated lazily (shared VectorStoreService inside)
        self._rag       = RAGAgent()
        self._quiz      = QuizAgent()
        self._summary   = SummaryAgent()
        self._flashcard = FlashcardAgent()
        self._teaching  = TeachingAgent()

    def route(
        self,
        user_id: int,
        message: str,
        doc_ids: list[int],
        doc_id: int | None = None,
        filename: str = "document",
        override_prefs: dict[str, Any] | None = None,
        # Quiz-specific
        question_type: str = "mcq",
        num_questions: int = 5,
        difficulty: str = "medium",
        topic: str | None = None,
        # Summary-specific
        style: str = "bullet",
        detail: str = "standard",
        # Flashcard-specific
        count: int = 10,
    ) -> dict[str, Any]:
        """
        Classify intent and dispatch to the correct agent.

        Args:
            user_id:       Authenticated user ID.
            message:       Raw user input (question / instruction).
            doc_ids:       List of document IDs in scope.
            doc_id:        Primary document ID (for quiz/summary/flashcard).
            filename:      Primary document filename.
            override_prefs: Override user preference dict.
            question_type: Quiz type hint.
            num_questions: Quiz question count.
            difficulty:    Quiz difficulty.
            topic:         Quiz topic filter.
            style:         Summary style.
            detail:        Summary detail level.
            count:         Flashcard count.

        Returns:
            Dict with at minimum: intent, agent_name, latency_ms
            Plus agent-specific keys (answer/summary/questions/flashcards/explanation).
        """
        total_start = time.perf_counter()

        # ── 1. Guardrails ──────────────────────────────────────────────────
        try:
            safe_message = validate_input(message)
        except ValueError as e:
            return {
                "intent":     "blocked",
                "agent_name": "guardrails",
                "error":      str(e),
                "answer":     str(e),
                "latency_ms": 0,
            }

        # ── 2. Classify intent ─────────────────────────────────────────────
        intent = classify_intent(safe_message)
        logger.info(
            "AgentRouter: user=%d intent=%s message='%s'",
            user_id, intent, safe_message[:60],
        )

        # ── 3. Dispatch ────────────────────────────────────────────────────
        result: dict[str, Any] = {}

        if intent == "ask":
            result = self._rag.run(
                user_id=user_id,
                question=safe_message,
                doc_ids=doc_ids,
                override_prefs=override_prefs,
            )

        elif intent == "quiz":
            _doc_id = doc_id or (doc_ids[0] if doc_ids else 0)
            result  = self._quiz.run(
                user_id=user_id,
                doc_id=_doc_id,
                filename=filename,
                question_type=question_type,
                num_questions=num_questions,
                difficulty=difficulty,
                topic=topic,
                override_prefs=override_prefs,
            )
            # Format quiz result as readable answer for chat UI
            q_count = result.get("num_questions", 0)
            result["answer"] = (
                f"✅ Generated {q_count} {question_type.upper()} questions. "
                f"Navigate to the Quiz page to take the quiz!"
            )

        elif intent == "summary":
            _doc_id = doc_id or (doc_ids[0] if doc_ids else 0)
            result  = self._summary.run(
                user_id=user_id,
                doc_id=_doc_id,
                filename=filename,
                style=style,
                detail=detail,
                override_prefs=override_prefs,
            )
            result["answer"] = result.get("summary", "Summary generated.")

        elif intent == "flashcard":
            _doc_id = doc_id or (doc_ids[0] if doc_ids else 0)
            result  = self._flashcard.run(
                user_id=user_id,
                doc_id=_doc_id,
                filename=filename,
                count=count,
            )
            fc_count = result.get("count", 0)
            result["answer"] = (
                f"🃏 Generated {fc_count} flashcards. "
                f"Navigate to the Flashcards page to review them!"
            )

        elif intent == "teach":
            result = self._teaching.run(
                user_id=user_id,
                concept=safe_message,
                doc_ids=doc_ids,
                override_prefs=override_prefs,
            )
            result["answer"] = result.get("explanation", "")

        total_ms = int((time.perf_counter() - total_start) * 1000)

        return {
            "intent":      intent,
            "intent_label": get_intent_description(intent),
            "agent_name":  _agent_name(intent),
            "sources":     result.get("sources", []),
            "answer":      result.get("answer", ""),
            "latency_ms":  total_ms,
            **result,
        }


def _agent_name(intent: str) -> str:
    return {
        "ask":       "RAGAgent",
        "quiz":      "QuizAgent",
        "summary":   "SummaryAgent",
        "flashcard": "FlashcardAgent",
        "teach":     "TeachingAgent",
    }.get(intent, "UnknownAgent")
