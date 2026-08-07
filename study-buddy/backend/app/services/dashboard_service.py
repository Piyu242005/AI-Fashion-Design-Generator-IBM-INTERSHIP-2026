"""
Dashboard Service — AI-Powered Study Buddy
============================================
Assembles the DashboardStats response by aggregating data
from multiple repositories and the AI recommendation engine.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repo import DocumentRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas import DashboardStats

logger = logging.getLogger("study_buddy.dashboard_service")

# Study time is tracked per chat session (approx 2 min per Q&A)
MINS_PER_CHAT = 2
WEAK_THRESHOLD   = 70   # % below this = weak
STRONG_THRESHOLD = 80   # % above this = strong


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._user_repo = UserRepository(db)
        self._doc_repo  = DocumentRepository(db)
        self._sess_repo = SessionRepository(db)

    async def get_stats(self, user_id: int) -> DashboardStats:
        """Build and return the full dashboard stats payload."""

        # Parallel data fetching
        docs        = await self._doc_repo.list_by_user(user_id)
        user        = await self._user_repo.get_by_id(user_id)
        recent_chats = await self._sess_repo.recent_chats(user_id, limit=5)
        avg_score   = await self._sess_repo.avg_quiz_score(user_id)
        quiz_count  = await self._sess_repo.quiz_count(user_id)
        topic_rows  = await self._sess_repo.all_topic_scores(user_id)
        total_chats = await self._sess_repo.total_chat_count(user_id)

        # Topic score map
        topic_scores = {row.topic: int(row.avg_score) for row in topic_rows}

        # Weak / strong topics
        weak_topics   = [t for t, s in topic_scores.items() if s < WEAK_THRESHOLD]
        strong_topics = [t for t, s in topic_scores.items() if s >= STRONG_THRESHOLD]

        # Study time estimate
        total_study_mins = total_chats * MINS_PER_CHAT

        # Streak (already on user model)
        streak = user.study_streak if user else 0

        # AI suggestions — simple rule-based for now (Phase 4 upgrades to Gemini)
        suggestions = _build_suggestions(weak_topics, avg_score, len(docs))

        # Recent activity feed
        recent_activity = _build_activity(docs, recent_chats, quiz_count)

        # Daily goal %  (target = 30 mins by default)
        daily_goal_mins = 30
        daily_goal_pct  = min(int((total_study_mins / daily_goal_mins) * 100), 100) \
                          if daily_goal_mins > 0 else 0

        # Format recent chats for UI
        chats_out = [
            {"question": c.question, "answer": c.answer, "created_at": str(c.created_at)}
            for c in recent_chats
        ]

        return DashboardStats(
            document_count=len(docs),
            total_study_mins=total_study_mins,
            avg_quiz_score=avg_score,
            study_streak=streak,
            weak_topics=weak_topics[:5],
            strong_topics=strong_topics[:5],
            ai_suggestions=suggestions,
            recent_chats=chats_out,
            recent_activity=recent_activity,
            topic_scores=topic_scores,
            flashcards_reviewed=0,      # updated in Phase 4
            daily_goal_pct=daily_goal_pct,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_suggestions(
    weak: list[str],
    avg: float,
    doc_count: int,
) -> list[str]:
    tips: list[str] = []
    if doc_count == 0:
        tips.append("📂 Upload your first study document to get started.")
    if weak:
        tips.append(f"⚠️ Focus on weak topics: {', '.join(weak[:3])}.")
    if avg < 60 and avg > 0:
        tips.append("📖 Your quiz average is below 60% — try reviewing your notes.")
    if avg >= 80:
        tips.append("🏆 Great job! Try a harder quiz to challenge yourself.")
    if not tips:
        tips.append("✅ Keep up the good work — consistency is key!")
    return tips[:3]


def _build_activity(docs: list, chats: list, quiz_count: int) -> list[dict]:
    activity = []
    for d in docs[:3]:
        activity.append({
            "icon": "📄",
            "text": f"Uploaded '{d.filename}'",
            "time": str(d.uploaded_at)[:16] if d.uploaded_at else "",
        })
    for c in chats[:2]:
        activity.append({
            "icon": "💬",
            "text": f"Asked: {c.question[:50]}…" if len(c.question) > 50 else f"Asked: {c.question}",
            "time": str(c.created_at)[:16] if c.created_at else "",
        })
    if quiz_count:
        activity.append({"icon": "❓", "text": f"Completed {quiz_count} quiz session(s)", "time": ""})
    return activity[:6]
