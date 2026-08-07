"""
Gemini Client — AI-Powered Study Buddy
========================================
LangChain-compatible Google Gemini wrapper.
Handles safety settings, retry logic, and response extraction.
"""

from __future__ import annotations

import logging
import time
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.exceptions import AIServiceError

logger = logging.getLogger("study_buddy.gemini")

# Gemini safety settings — block medium and above for student safety
_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",  "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HARASSMENT",         "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",  "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


@lru_cache(maxsize=1)
def get_gemini_llm() -> ChatGoogleGenerativeAI:
    """Return a cached Gemini LLM instance."""
    if not settings.GOOGLE_API_KEY:
        raise AIServiceError("GOOGLE_API_KEY is not configured.")

    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.GEMINI_TEMPERATURE,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        safety_settings=_SAFETY_SETTINGS,
        convert_system_message_to_human=True,  # Gemini requires this
    )


def invoke_with_retry(
    chain,
    inputs: dict,
    max_retries: int = 3,
    backoff: float = 2.0,
) -> str:
    """
    Invoke a LangChain chain with exponential backoff retry.

    Args:
        chain:       LangChain runnable (prompt | llm | parser).
        inputs:      Dict of template variables.
        max_retries: Maximum retry attempts.
        backoff:     Base backoff multiplier in seconds.

    Returns:
        String response from the LLM.

    Raises:
        AIServiceError: If all retries fail.
    """
    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            result = chain.invoke(inputs)
            # Handle both AIMessage and plain string outputs
            if hasattr(result, "content"):
                return str(result.content)
            return str(result)
        except Exception as exc:
            last_err = exc
            if attempt < max_retries:
                wait = backoff ** attempt
                logger.warning(
                    "Gemini attempt %d/%d failed (%s) — retrying in %.1fs",
                    attempt, max_retries, type(exc).__name__, wait,
                )
                time.sleep(wait)
            else:
                logger.error("All %d Gemini retries failed: %s", max_retries, exc)

    raise AIServiceError(f"AI service failed after {max_retries} attempts: {last_err}")
