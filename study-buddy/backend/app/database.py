"""
Database — AI-Powered Study Buddy
====================================
SQLAlchemy async engine + session factory for SQLite.
Uses aiosqlite driver for non-blocking DB operations in FastAPI.

Tables are created on startup via create_all().
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ---------------------------------------------------------------------------
# Declarative base — all ORM models inherit from this
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Async engine
# ---------------------------------------------------------------------------

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,              # SQL logging in dev mode
    connect_args={"check_same_thread": False},  # SQLite-specific
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# DB initialisation — called once on app startup
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables if they don't exist."""
    # Import models so SQLAlchemy registers them before create_all
    import app.models  # noqa: F401 — side-effect import

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
