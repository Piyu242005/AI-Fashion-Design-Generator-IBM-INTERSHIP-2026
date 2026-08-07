"""
Performance Tests — AI-Powered Study Buddy
============================================
Benchmarks for text processing, splitting, and intent classification.
These are fast, in-process benchmarks — no API calls or LLM calls.
Uses pytest-benchmark if available, else plain timeit assertions.
"""

from __future__ import annotations

import time
import pytest

from app.ai.intent_classifier import classify_intent
from app.utils.text_splitter import split_text


# ---------------------------------------------------------------------------
# Text Splitter performance
# ---------------------------------------------------------------------------

LARGE_TEXT = """
Machine learning is a method of data analysis that automates analytical model building.
Based on the idea that systems can learn from data, identify patterns and make decisions
with minimal human intervention. This is a comprehensive overview of the field.
""" * 200  # ~200 paragraphs — simulates a medium-sized PDF


class TestTextSplitterPerformance:
    def test_splits_large_text_under_2_seconds(self):
        start = time.perf_counter()
        chunks = split_text(LARGE_TEXT, source="perf_test.txt")
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"Splitting took {elapsed:.2f}s — expected < 2.0s"
        assert len(chunks) > 0

    def test_100_small_splits_under_1_second(self):
        small = "This is a short text about science and technology. " * 20
        start = time.perf_counter()
        for _ in range(100):
            split_text(small, source="small.txt")
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"100 small splits took {elapsed:.2f}s"


# ---------------------------------------------------------------------------
# Intent classifier performance
# ---------------------------------------------------------------------------

class TestIntentClassifierPerformance:
    MESSAGES = [
        "What is photosynthesis?",
        "Generate a quiz on Newton's laws",
        "Summarize my chemistry notes",
        "Create flashcards from chapter 5",
        "Explain quantum mechanics simply",
    ] * 200  # 1000 classifications

    def test_1000_classifications_under_1_second(self):
        start = time.perf_counter()
        for msg in self.MESSAGES:
            classify_intent(msg)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"1000 classifications took {elapsed:.2f}s"

    def test_single_classification_under_10ms(self):
        start = time.perf_counter()
        classify_intent("What is the speed of light?")
        elapsed = (time.perf_counter() - start) * 1000  # ms
        assert elapsed < 10.0, f"Single classification took {elapsed:.2f}ms"


# ---------------------------------------------------------------------------
# Password hashing performance
# ---------------------------------------------------------------------------

class TestSecurityPerformance:
    def test_bcrypt_hash_under_500ms(self):
        """bcrypt is intentionally slow — but should be < 500ms per hash."""
        from app.core.security import hash_password
        start = time.perf_counter()
        hash_password("test_password_12345")
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500, f"bcrypt took {elapsed:.0f}ms — too slow"

    def test_jwt_create_decode_under_50ms(self):
        from app.core.security import create_access_token, decode_access_token
        start = time.perf_counter()
        for _ in range(100):
            token = create_access_token({"sub": "1"})
            decode_access_token(token)
        elapsed = (time.perf_counter() - start) * 1000
        avg = elapsed / 100
        assert avg < 50, f"JWT create+decode avg {avg:.2f}ms — too slow"
