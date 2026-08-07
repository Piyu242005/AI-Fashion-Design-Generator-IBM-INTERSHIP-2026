"""
Dashboard Service — AI-Powered Study Buddy (Upgraded with Recommendation Engine)
==================================================================================
Assembles DashboardStats by aggregating from repositories
and calling the RecommendationEngine for AI-powered suggestions.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repo import DocumentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas import DashboardStats
from app.services.recommendation_service import RecommendationEngine

logger = logging.getLogger("study_buddy.dashboard_service")

MINS_PER_CHAT = 2


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._user_repo = UserRepository(db)
        self._doc_repo  = DocumentRepository(db)
        self._sess_repo = SessionRepository(db)
        self._rec_engine = RecommendationEngine(db)

    async def get_stats(self, user_id: int) -> DashboardStats:
        """Build and return the full dashboard stats payload."""

        # ── Fetch raw data ─────────────────────────────────────────────────
        docs         = await self._doc_repo.list_by_user(user_id)
        user         = await self._user_repo.get_by_id(user_id)
        recent_chats = await self._sess_repo.recent_chats(user_id, limit=5)
        avg_score    = await self._sess_repo.avg_quiz_score(user_id)
        quiz_count   = await self._sess_repo.quiz_count(user_id)
        total_chats  = await self._sess_repo.total_chat_count(user_id)
        streak       = user.study_streak if user else 0

        # ── AI Recommendations (from RecommendationEngine) ─────────────────
        rec = await self._rec_engine.get_recommendations(
            user_id=user_id,
            doc_count=len(docs),
            study_streak=streak,
        )

        # ── Study time estimate ────────────────────────────────────────────
        total_study_mins = total_chats * MINS_PER_CHAT

        # ── Daily goal % ───────────────────────────────────────────────────
        daily_goal_mins = 30
        daily_goal_pct  = min(int((total_study_mins / daily_goal_mins) * 100), 100)

        # ── Activity feed ──────────────────────────────────────────────────
        recent_activity = _build_activity(docs, recent_chats, quiz_count)

        # ── Format recent chats ────────────────────────────────────────────
        chats_out = [
            {
                "question":   c.question,
                "answer":     c.answer,
                "intent":     c.intent,
                "created_at": str(c.created_at),
            }
            for c in recent_chats
        ]

        return DashboardStats(
            document_count=len(docs),
            total_study_mins=total_study_mins,
            avg_quiz_score=avg_score,
            study_streak=streak,
            weak_topics=rec["weak_topics"],
            strong_topics=rec["strong_topics"],
            ai_suggestions=rec["suggestions"],
            recent_chats=chats_out,
            recent_activity=recent_activity,
            topic_scores={t: int(s) for t, s in rec["topic_scores"].items()},
            flashcards_reviewed=0,
            daily_goal_pct=daily_goal_pct,
        )


def _build_activity(docs, chats, quiz_count: int) -> list[dict]:
    activity = []
    for d in docs[:3]:
        activity.append({
            "icon": "📄",
            "text": f"Uploaded '{d.filename}'",
            "time": str(d.uploaded_at)[:16] if d.uploaded_at else "",
        })
    for c in chats[:2]:
        q_short = c.question[:50] + "…" if len(c.question) > 50 else c.question
        activity.append({
            "icon": "💬",
            "text": f"Asked: {q_short}",
            "time": str(c.created_at)[:16] if c.created_at else "",
        })
    if quiz_count:
        activity.append({
            "icon": "❓",
            "text": f"Completed {quiz_count} quiz session(s)",
            "time": "",
        })
    return activity[:6]
