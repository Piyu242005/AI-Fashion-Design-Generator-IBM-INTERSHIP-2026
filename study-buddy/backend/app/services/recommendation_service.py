"""
Recommendation Engine — AI-Powered Study Buddy
================================================
Analyses a student's quiz performance data and generates
personalised study recommendations using Gemini.

Pipeline:
  1. Pull topic scores from SQLite (via SessionRepository)
  2. Identify weak topics (score < 70%)
  3. Build a personalised recommendation prompt
  4. Invoke Gemini for AI-generated study advice
  5. Return structured recommendations + auto-practice quiz topics

This is the "intelligent" part of the dashboard — it turns
raw score data into actionable learning guidance.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import async_invoke_with_retry, get_gemini_llm
from app.guardrails import validate_output
from app.repositories.session_repo import SessionRepository

logger = logging.getLogger("study_buddy.recommendation")

# ---------------------------------------------------------------------------
# In-process TTL cache — prevents repeated Gemini calls on every dashboard load
# ---------------------------------------------------------------------------
_REC_CACHE: dict[int, tuple[float, dict[str, Any]]] = {}  # {user_id: (timestamp, result)}
_REC_CACHE_TTL_SECONDS: int = 300  # 5-minute TTL — refreshes after meaningful activity

# ---------------------------------------------------------------------------
# Prompt Template
# ---------------------------------------------------------------------------

_REC_SYSTEM = """You are an expert academic coach and learning strategist.
Analyse the student's quiz performance data and provide specific, actionable
study recommendations. Be encouraging but honest."""

_REC_HUMAN = """Student Performance Data:
---
{performance_data}
---

Total documents uploaded: {doc_count}
Study streak: {streak} days
Average quiz score: {avg_score}%

Based on this data, provide:
1. **Top 3 Priority Topics** to study (with brief explanation why)
2. **Study Strategy** (specific techniques for the weak areas)
3. **Motivational Message** (1-2 sentences, encouraging)
4. **Next Steps** (3 concrete actions the student should take)

Keep each section concise and actionable."""

_REC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _REC_SYSTEM),
    ("human",  _REC_HUMAN),
])

WEAK_THRESHOLD   = 70   # % — below this = weak topic
STRONG_THRESHOLD = 80   # % — above this = strong topic


class RecommendationEngine:
    """
    AI-powered personalised study recommendation engine.

    Reads quiz performance history and generates tailored advice
    using Gemini, adapting to each student's strengths and weaknesses.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = SessionRepository(db)

    async def get_recommendations(
        self,
        user_id: int,
        doc_count: int = 0,
        study_streak: int = 0,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Generate personalised recommendations for a user.

        Results are cached for _REC_CACHE_TTL_SECONDS (5 min) per user to avoid
        calling Gemini on every dashboard page load.

        Args:
            user_id:       Authenticated user ID.
            doc_count:     Number of documents uploaded (for context).
            study_streak:  Current study streak in days.
            force_refresh: Bypass cache and regenerate immediately.

        Returns:
            Dict with keys:
                ai_text         — Gemini-generated recommendation text
                weak_topics     — List of weak topic names
                strong_topics   — List of strong topic names
                topic_scores    — Dict of topic → avg_score
                avg_score       — Overall average quiz score
                priority_topics — Top 3 topics to focus on
        """
        # ── 0. Cache hit — return early if still fresh ─────────────────────
        if not force_refresh and user_id in _REC_CACHE:
            cached_ts, cached_result = _REC_CACHE[user_id]
            if time.monotonic() - cached_ts < _REC_CACHE_TTL_SECONDS:
                logger.debug("Recommendation cache hit for user_id=%d", user_id)
                return cached_result

        # ── 1. Pull performance data ───────────────────────────────────────
        topic_rows  = await self._repo.all_topic_scores(user_id)
        avg_score   = await self._repo.avg_quiz_score(user_id)

        topic_scores  = {row.topic: round(row.avg_score, 1) for row in topic_rows}
        weak_topics   = [t for t, s in topic_scores.items() if s < WEAK_THRESHOLD]
        strong_topics = [t for t, s in topic_scores.items() if s >= STRONG_THRESHOLD]

        # ── 2. Build performance summary for prompt ────────────────────────
        if topic_scores:
            lines = [
                f"• {topic}: {score}% ({'⚠ WEAK' if score < WEAK_THRESHOLD else '✓ GOOD'})"
                for topic, score in sorted(topic_scores.items(), key=lambda x: x[1])
            ]
            performance_data = "\n".join(lines)
        else:
            performance_data = "No quiz results yet — student has not taken any quizzes."

        # ── 3. Invoke Gemini for recommendations ───────────────────────────
        ai_text = ""
        if topic_scores:  # Only call AI if there's data to analyse
            try:
                chain   = _REC_PROMPT | get_gemini_llm() | StrOutputParser()
                raw     = await async_invoke_with_retry(chain, {
                    "performance_data": performance_data,
                    "doc_count":        doc_count,
                    "streak":           study_streak,
                    "avg_score":        avg_score,
                })
                ai_text = validate_output(raw)
            except Exception as e:
                logger.warning("Recommendation AI call failed: %s", e)
                ai_text = ""

        # ── 4. Rule-based fallback suggestions ────────────────────────────
        suggestions = _rule_based_suggestions(weak_topics, avg_score, doc_count)
        if ai_text:
            # Use AI text as primary, rules as structured metadata
            suggestions = [ai_text[:500]] + suggestions[:1]

        priority_topics = sorted(
            weak_topics, key=lambda t: topic_scores.get(t, 0)
        )[:3]

        logger.info(
            "Recommendations generated for user_id=%d: %d weak, %d strong topics",
            user_id, len(weak_topics), len(strong_topics),
        )

        result: dict[str, Any] = {
            "ai_text":        ai_text,
            "suggestions":    suggestions,
            "weak_topics":    weak_topics[:5],
            "strong_topics":  strong_topics[:5],
            "topic_scores":   topic_scores,
            "avg_score":      avg_score,
            "priority_topics": priority_topics,
        }
        # ── Store in TTL cache ─────────────────────────────────────────────
        _REC_CACHE[user_id] = (time.monotonic(), result)
        return result


# ---------------------------------------------------------------------------
# Rule-based fallback (works without Gemini)
# ---------------------------------------------------------------------------

def _rule_based_suggestions(
    weak: list[str],
    avg: float,
    doc_count: int,
) -> list[str]:
    tips: list[str] = []
    if doc_count == 0:
        tips.append("📂 Start by uploading your study notes or textbook chapters.")
        return tips
    if not weak:
        if avg >= 80:
            tips.append("🏆 Excellent performance! Try harder quiz difficulty to challenge yourself.")
        else:
            tips.append("📖 Take quizzes on your uploaded documents to identify areas to improve.")
        return tips
    tips.append(f"⚠️ Focus on: {', '.join(weak[:3])} — these topics scored below 70%.")
    if avg < 50:
        tips.append("📚 Consider re-reading your notes before taking more quizzes.")
    elif avg < 70:
        tips.append("💡 Use the Flashcards feature to reinforce key terms in weak topics.")
    tips.append("🔄 Re-take quizzes on weak topics after reviewing your notes.")
    return tips[:3]
