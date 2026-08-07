"""
Memory Manager — AI-Powered Study Buddy
=========================================
Manages all five memory types for personalised, context-aware AI responses.

Memory Types
------------
1. Session Memory       — In-process ConversationBufferWindowMemory (last 10 turns)
2. Conversation Memory  — SQLite chat_history (full persistent history)
3. User Preference Memory — session_state / SQLite user_preferences
4. Study History        — SQLite study_sessions / documents
5. Weak Topic Memory    — SQLite topic_scores (drives recommendations)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("study_buddy.memory")


# ---------------------------------------------------------------------------
# Lightweight in-process window memory (replaces deprecated langchain.memory)
# ---------------------------------------------------------------------------

class _SimpleWindowMemory:
    """
    Minimal drop-in replacement for ConversationBufferWindowMemory.
    Stores the last *k* (question, answer) pairs in a plain list.
    No external dependencies — no LangChain memory module required.
    """

    def __init__(self, k: int = 10) -> None:
        self.k = k
        self._turns: list[tuple[str, str]] = []   # [(question, answer), ...]

    def save_context(self, inputs: dict, outputs: dict) -> None:
        self._turns.append((inputs.get("input", ""), outputs.get("output", "")))
        if len(self._turns) > self.k:
            self._turns = self._turns[-self.k:]

    def clear(self) -> None:
        self._turns.clear()

    @property
    def messages(self) -> list[dict[str, str]]:
        """Return turns as a list of {type, content} dicts (mimics LangChain API)."""
        out = []
        for q, a in self._turns:
            out.append({"type": "human",  "content": q})
            out.append({"type": "ai",     "content": a})
        return out


# ---------------------------------------------------------------------------
# 1. Session Memory (in-process, per-user dict keyed by user_id)
# ---------------------------------------------------------------------------

_session_memories: dict[int, _SimpleWindowMemory] = {}


def get_session_memory(user_id: int, k: int = 10) -> _SimpleWindowMemory:
    """
    Return (or create) a window memory for *user_id*.

    Keeps the last *k* human/AI turn pairs in RAM.
    Automatically cleared on server restart (ephemeral).
    """
    if user_id not in _session_memories:
        _session_memories[user_id] = _SimpleWindowMemory(k=k)
        logger.debug("Created session memory for user_id=%d", user_id)
    return _session_memories[user_id]


def save_to_session_memory(user_id: int, question: str, answer: str) -> None:
    """Add a Q&A turn to the session memory for *user_id*."""
    mem = get_session_memory(user_id)
    mem.save_context({"input": question}, {"output": answer})
    logger.debug("Session memory updated for user_id=%d", user_id)


def clear_session_memory(user_id: int) -> None:
    """Clear the in-process session memory for *user_id*."""
    if user_id in _session_memories:
        _session_memories[user_id].clear()
        logger.info("Session memory cleared for user_id=%d", user_id)


def get_session_history_str(user_id: int) -> str:
    """
    Return the current session memory as a formatted string
    suitable for injection into a LangChain prompt.
    """
    mem = get_session_memory(user_id)
    messages = mem.messages
    if not messages:
        return "No conversation history yet."

    lines: list[str] = []
    for msg in messages:
        role = "Student" if msg["type"] == "human" else "StudyBuddy"
        lines.append(f"{role}: {msg['content'][:300]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Conversation Memory — persistent (pulled from DB in services)
# ---------------------------------------------------------------------------
# Handled by SessionRepository.recent_chats() — see rag_service.py

# ---------------------------------------------------------------------------
# 3. User Preference Memory
# ---------------------------------------------------------------------------

DEFAULT_PREFERENCES: dict[str, Any] = {
    "ai_style":      "Standard",
    "explain_level": "Intermediate",
    "language":      "English",
    "quiz_diff":     "Medium",
    "qtype":         "MCQ",
    "qcount":        5,
    "daily_goal":    30,
    "memory_depth":  10,
    "theme":         "Dark",
}

# In-process cache keyed by user_id
_user_prefs: dict[int, dict[str, Any]] = {}


def get_user_preferences(user_id: int) -> dict[str, Any]:
    """Return cached user preferences, falling back to defaults."""
    return _user_prefs.get(user_id, DEFAULT_PREFERENCES.copy())


def set_user_preferences(user_id: int, prefs: dict[str, Any]) -> None:
    """Update cached user preferences."""
    _user_prefs[user_id] = {**DEFAULT_PREFERENCES, **prefs}
    logger.debug("Preferences updated for user_id=%d", user_id)


# ---------------------------------------------------------------------------
# 4 & 5. Study History + Weak Topic Memory — handled by repositories
# ---------------------------------------------------------------------------
# DocumentRepository.list_by_user()   → study history
# SessionRepository.all_topic_scores() → weak topic memory
# These are accessed directly in DashboardService and RecommendationService
