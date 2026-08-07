"""
User Repository — AI-Powered Study Buddy
==========================================
Data access layer for User model.
Follows the Repository Pattern — business logic stays in services.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, name: str, email: str, hashed_password: str) -> User:
        user = User(name=name, email=email, hashed_password=hashed_password)
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def update_streak(self, user: User, streak: int) -> User:
        user.study_streak = streak
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def count_documents(self, user_id: int) -> int:
        """Return document count via SELECT COUNT(*) — avoids full row fetch."""
        from app.models import Document
        result = await self._db.execute(
            select(func.count()).select_from(Document).where(Document.user_id == user_id)
        )
        return result.scalar_one()
