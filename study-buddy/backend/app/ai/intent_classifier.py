"""
Intent Classifier — AI-Powered Study Buddy
============================================
Classifies a user's message into one of five intents using
keyword matching + semantic fallback. Routes to the correct agent.

Intent Taxonomy
---------------
  ask        → RAG Agent      (Q&A from documents)
  quiz       → Quiz Agent     (generate quiz questions)
  summary    → Summary Agent  (summarise documents)
  flashcard  → Flashcard Agent (create flashcards)
  teach      → Teaching Agent (explain concepts simply)
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger("study_buddy.intent")

# ---------------------------------------------------------------------------
# Keyword → intent maps (ordered: more specific first)
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "quiz": [
        "quiz", "test me", "test my", "mcq", "multiple choice",
        "true or false", "true/false", "practice question",
        "question paper", "exam question", "generate question",
    ],
    "summary": [
        "summarize", "summarise", "summary", "brief", "overview",
        "key points", "main points", "condense", "tldr", "tl;dr",
        "short version", "gist",
    ],
    "flashcard": [
        "flashcard", "flash card", "flash-card", "term", "vocabulary",
        "key terms", "definition card", "study card", "memorize",
    ],
    "teach": [
        "explain simply", "explain like", "eli5", "what is",
        "teach me", "how does", "why does", "concept of",
        "in simple words", "in simple terms", "analogy",
        "break it down", "layman",
    ],
    # "ask" is the default — any question not matching above
    "ask": [
        "what", "how", "why", "when", "where", "who", "which",
        "tell me", "describe", "define", "list", "give me",
        "explain", "show me", "find", "search",
    ],
}

# Compiled patterns for speed
_COMPILED: dict[str, re.Pattern] = {
    intent: re.compile(
        "|".join(re.escape(kw) for kw in keywords),
        re.IGNORECASE,
    )
    for intent, keywords in _INTENT_KEYWORDS.items()
}

# Priority order (quiz/summary/flashcard/teach checked before generic ask)
_PRIORITY_ORDER = ["quiz", "summary", "flashcard", "teach", "ask"]


def classify_intent(message: str) -> str:
    """
    Classify a user message into an intent string.

    Args:
        message: Raw user input string.

    Returns:
        One of: 'ask' | 'quiz' | 'summary' | 'flashcard' | 'teach'
    """
    text = message.strip().lower()

    # Check high-priority intents first
    for intent in _PRIORITY_ORDER[:-1]:  # everything except 'ask'
        if _COMPILED[intent].search(text):
            logger.debug("Intent classified as '%s' for: %s", intent, message[:60])
            return intent

    # Default
    logger.debug("Intent classified as 'ask' (default) for: %s", message[:60])
    return "ask"


def get_intent_description(intent: str) -> str:
    """Return a human-readable description of an intent."""
    descriptions = {
        "ask":       "Question answering from your documents",
        "quiz":      "Quiz generation",
        "summary":   "Document summarisation",
        "flashcard": "Flashcard creation",
        "teach":     "Concept explanation",
    }
    return descriptions.get(intent, "General assistance")
