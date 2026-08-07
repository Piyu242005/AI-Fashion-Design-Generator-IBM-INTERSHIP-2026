"""
ORM Models — AI-Powered Study Buddy
=====================================
SQLAlchemy async ORM model definitions.
All models inherit from Base (defined in database.py).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    name:            Mapped[str]      = mapped_column(String(120), nullable=False)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]      = mapped_column(String(255), nullable=False)
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    study_streak:    Mapped[int]      = mapped_column(Integer, default=0)
    last_active_date:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Relationships
    documents:    Mapped[list["Document"]]    = relationship("Document",   back_populates="user", cascade="all, delete-orphan")
    chat_history: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    quiz_results: Mapped[list["QuizResult"]]  = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")
    topic_scores: Mapped[list["TopicScore"]]  = relationship("TopicScore", back_populates="user", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(Base):
    __tablename__ = "documents"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    user_id:     Mapped[int]      = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    filename:    Mapped[str]      = mapped_column(String(255), nullable=False)
    file_type:   Mapped[str]      = mapped_column(String(10),  nullable=False)
    file_path:   Mapped[str]      = mapped_column(String(512), nullable=False)
    file_size_kb:Mapped[int]      = mapped_column(Integer, default=0)
    chunk_count: Mapped[int]      = mapped_column(Integer, default=0)
    chroma_ids:  Mapped[str]      = mapped_column(Text, default="")   # JSON list
    status:      Mapped[str]      = mapped_column(String(20), default="processing")  # processing|ready|error
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship("User", back_populates="documents")
    chat_history: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="document")


# ---------------------------------------------------------------------------
# Chat History
# ---------------------------------------------------------------------------

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    user_id:     Mapped[int]      = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    question:    Mapped[str]      = mapped_column(Text, nullable=False)
    answer:      Mapped[str]      = mapped_column(Text, nullable=False)
    sources:     Mapped[str]      = mapped_column(Text, default="")   # JSON list of source refs
    intent:      Mapped[str]      = mapped_column(String(30), default="ask")  # ask|quiz|summary|flashcard|teach
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user:     Mapped["User"]     = relationship("User",     back_populates="chat_history")
    document: Mapped["Document"] = relationship("Document", back_populates="chat_history")


# ---------------------------------------------------------------------------
# Quiz Result
# ---------------------------------------------------------------------------

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    user_id:     Mapped[int]      = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[int]      = mapped_column(ForeignKey("documents.id"), nullable=False)
    topic:       Mapped[str]      = mapped_column(String(120), default="General")
    score_pct:   Mapped[float]    = mapped_column(Float, nullable=False)
    num_questions: Mapped[int]    = mapped_column(Integer, nullable=False)
    question_type: Mapped[str]    = mapped_column(String(30), default="mcq")
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship("User", back_populates="quiz_results")


# ---------------------------------------------------------------------------
# Topic Score (aggregate — updated after every quiz)
# ---------------------------------------------------------------------------

class TopicScore(Base):
    __tablename__ = "topic_scores"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    topic:      Mapped[str]      = mapped_column(String(120), nullable=False)
    avg_score:  Mapped[float]    = mapped_column(Float, default=0.0)
    attempts:   Mapped[int]      = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    user: Mapped["User"] = relationship("User", back_populates="topic_scores")
