"""
Input / Output Guardrails — AI-Powered Study Buddy
====================================================
Validates and sanitises user inputs and AI outputs.
Implements responsible AI practices:
  - Prompt injection protection
  - PII detection
  - Toxicity keyword filter
  - Output length validation
"""

from __future__ import annotations

import re
import logging

logger = logging.getLogger("study_buddy.guardrails")

# ---------------------------------------------------------------------------
# Prompt injection patterns
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?instructions",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(if\s+)?you\s+are",
    r"jailbreak",
    r"DAN\s+mode",
    r"override\s+system",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

# ---------------------------------------------------------------------------
# PII patterns (for document scanning before indexing)
# ---------------------------------------------------------------------------
_PII_PATTERNS = {
    "email":        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone_in":     re.compile(r"\b[6-9]\d{9}\b"),                          # India mobile
    "aadhaar":      re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "pan":          re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "credit_card":  re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}

# ---------------------------------------------------------------------------
# Toxicity keyword list (extend as needed)
# ---------------------------------------------------------------------------
_TOXIC_WORDS: set[str] = {
    "hate", "kill", "murder", "suicide", "bomb", "terror",
    "explicit", "pornography",
}


def check_prompt_injection(text: str) -> str:
    """
    Detect and sanitise potential prompt injection attacks.

    Returns:
        Sanitised text.

    Raises:
        ValueError: If injection pattern detected (block the request).
    """
    if _INJECTION_RE.search(text):
        logger.warning("Prompt injection attempt detected: %s", text[:80])
        raise ValueError("Your input contains disallowed patterns. Please rephrase.")
    return text


def detect_pii(text: str) -> dict[str, list[str]]:
    """
    Scan text for PII patterns.

    Returns:
        Dict mapping PII type → list of found matches.
    """
    found: dict[str, list[str]] = {}
    for pii_type, pattern in _PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[pii_type] = matches
    return found


def redact_pii(text: str) -> str:
    """Replace detected PII with [REDACTED] placeholders."""
    for pii_type, pattern in _PII_PATTERNS.items():
        text = pattern.sub(f"[{pii_type.upper()}_REDACTED]", text)
    return text


def check_toxicity(text: str) -> None:
    """
    Basic toxicity check against keyword blocklist.

    Raises:
        ValueError: If toxic content detected.
    """
    lower = text.lower()
    hits  = [w for w in _TOXIC_WORDS if w in lower]
    if hits:
        logger.warning("Toxic content detected: %s", hits)
        raise ValueError("Your input contains inappropriate content. Please keep questions educational.")


def validate_input(text: str) -> str:
    """
    Run all input guardrails in sequence.

    Returns:
        Cleaned, safe input text.

    Raises:
        ValueError: If any check fails.
    """
    check_toxicity(text)
    clean = check_prompt_injection(text)
    return clean.strip()


def validate_output(text: str, max_chars: int = 8000) -> str:
    """
    Validate and truncate AI output if necessary.

    Returns:
        Validated output string.
    """
    if not text or not text.strip():
        return "I was unable to generate a response. Please try again."
    return text[:max_chars].strip()
