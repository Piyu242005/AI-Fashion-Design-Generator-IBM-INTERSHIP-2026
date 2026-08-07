"""
Session Repository — AI-Powered Study Buddy
=============================================
Data access for ChatHistory, QuizResult, and TopicScore tables.
"""

from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatHistory, QuizResult, TopicScore


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Chat history ───────────────────────────────────────────────────────

    async def save_chat(
        self,
        user_id: int,
        document_id: int | None,
        question: str,
        answer: str,
        sources: str = "[]",
        intent: str = "ask",
    ) -> ChatHistory:
        record = ChatHistory(
            user_id=user_id,
            document_id=document_id,
            question=question,
            answer=answer,
            sources=sources,
            intent=intent,
        )
        self._db.add(record)
        await self._db.commit()
        await self._db.refresh(record)
        return record

    async def recent_chats(self, user_id: int, limit: int = 5) -> list[ChatHistory]:
        result = await self._db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def total_chat_count(self, user_id: int) -> int:
        result = await self._db.execute(
            select(func.count(ChatHistory.id)).where(ChatHistory.user_id == user_id)
        )
        return result.scalar_one() or 0

    # ── Quiz results ───────────────────────────────────────────────────────

    async def save_quiz_result(
        self,
        user_id: int,
        document_id: int,
        topic: str,
        score_pct: float,
        num_questions: int,
        question_type: str,
    ) -> QuizResult:
        record = QuizResult(
            user_id=user_id,
            document_id=document_id,
            topic=topic,
            score_pct=score_pct,
            num_questions=num_questions,
            question_type=question_type,
        )
        self._db.add(record)
        await self._db.commit()
        return record

    async def avg_quiz_score(self, user_id: int) -> float:
        result = await self._db.execute(
            select(func.avg(QuizResult.score_pct)).where(QuizResult.user_id == user_id)
        )
        return round(result.scalar_one() or 0.0, 1)

    async def quiz_count(self, user_id: int) -> int:
        result = await self._db.execute(
            select(func.count(QuizResult.id)).where(QuizResult.user_id == user_id)
        )
        return result.scalar_one() or 0

    # ── Topic scores ───────────────────────────────────────────────────────

    async def upsert_topic_score(
        self,
        user_id: int,
        topic: str,
        new_score: float,
    ) -> TopicScore:
        result = await self._db.execute(
            select(TopicScore)
            .where(TopicScore.user_id == user_id, TopicScore.topic == topic)
        )
        record = result.scalar_one_or_none()

        if record is None:
            record = TopicScore(user_id=user_id, topic=topic,
                                avg_score=new_score, attempts=1)
            self._db.add(record)
        else:
            # Weighted running average
            record.avg_score = round(
                (record.avg_score * record.attempts + new_score) / (record.attempts + 1), 1
            )
            record.attempts += 1

        await self._db.commit()
        await self._db.refresh(record)
        return record

    async def all_topic_scores(self, user_id: int) -> list[TopicScore]:
        result = await self._db.execute(
            select(TopicScore).where(TopicScore.user_id == user_id)
        )
        return list(result.scalars().all())
