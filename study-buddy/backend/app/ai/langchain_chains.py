"""
LangChain Chains — AI-Powered Study Buddy
==========================================
Pre-built, reusable LangChain LCEL chains for every AI feature.
Each chain: PromptTemplate | ChatGoogleGenerativeAI | OutputParser

LCEL (LangChain Expression Language) gives us:
  - Streaming support
  - Automatic retry via invoke_with_retry
  - Easy composition and testing
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser

from app.ai.gemini_client import get_gemini_llm
from app.prompts import (
    FLASHCARD_PROMPT,
    QUIZ_MCQ_PROMPT,
    QUIZ_SA_PROMPT,
    QUIZ_TF_PROMPT,
    RAG_PROMPT,
    SUMMARY_BULLET_PROMPT,
    SUMMARY_PARAGRAPH_PROMPT,
    TEACHING_PROMPT,
)


def _build_chain(prompt):
    """Build a basic prompt | llm | str_parser chain."""
    return prompt | get_gemini_llm() | StrOutputParser()


def get_rag_chain():
    """RAG Q&A chain — uses context + question + history."""
    return _build_chain(RAG_PROMPT)


def get_summary_bullet_chain():
    """Bullet-point summary chain."""
    return _build_chain(SUMMARY_BULLET_PROMPT)


def get_summary_paragraph_chain():
    """Paragraph summary chain."""
    return _build_chain(SUMMARY_PARAGRAPH_PROMPT)


def get_quiz_mcq_chain():
    """MCQ quiz generation chain."""
    return _build_chain(QUIZ_MCQ_PROMPT)


def get_quiz_tf_chain():
    """True/False quiz generation chain."""
    return _build_chain(QUIZ_TF_PROMPT)


def get_quiz_sa_chain():
    """Short-answer quiz generation chain."""
    return _build_chain(QUIZ_SA_PROMPT)


def get_flashcard_chain():
    """Flashcard generation chain."""
    return _build_chain(FLASHCARD_PROMPT)


def get_teaching_chain():
    """Concept explanation (Teaching Agent) chain."""
    return _build_chain(TEACHING_PROMPT)
