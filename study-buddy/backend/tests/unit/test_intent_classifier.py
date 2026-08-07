"""
Unit Tests — Intent Classifier
================================
Tests for the AI agent routing intent classification logic.
"""

from __future__ import annotations

import pytest

from app.ai.intent_classifier import classify_intent, get_intent_description


class TestIntentClassifier:

    # ── Quiz intent ────────────────────────────────────────────────────────
    @pytest.mark.parametrize("msg", [
        "Generate a quiz on photosynthesis",
        "Create MCQ questions from my notes",
        "Test me on chapter 3",
        "Give me some practice questions",
        "I want to test my knowledge",
    ])
    def test_quiz_intent(self, msg: str):
        assert classify_intent(msg) == "quiz"

    # ── Summary intent ─────────────────────────────────────────────────────
    @pytest.mark.parametrize("msg", [
        "Summarize my notes on DNA replication",
        "Give me an overview of this chapter",
        "What are the key points in this document?",
        "TL;DR of the uploaded file",
        "Condense this into bullet points",
    ])
    def test_summary_intent(self, msg: str):
        assert classify_intent(msg) == "summary"

    # ── Flashcard intent ───────────────────────────────────────────────────
    @pytest.mark.parametrize("msg", [
        "Create flashcards for key terms",
        "Make flash cards from this document",
        "Generate vocabulary cards",
        "I want to memorize the definitions",
    ])
    def test_flashcard_intent(self, msg: str):
        assert classify_intent(msg) == "flashcard"

    # ── Teaching intent ────────────────────────────────────────────────────
    @pytest.mark.parametrize("msg", [
        "Explain simply what osmosis is",
        "ELI5 quantum entanglement",
        "Teach me about photosynthesis",
        "Break it down for me",
        "Explain this in simple words",
    ])
    def test_teach_intent(self, msg: str):
        assert classify_intent(msg) == "teach"

    # ── Ask intent (default) ───────────────────────────────────────────────
    @pytest.mark.parametrize("msg", [
        "What is the speed of light?",
        "How does DNA replication work?",
        "Who discovered penicillin?",
        "List the planets in the solar system",
        "Define mitosis",
    ])
    def test_ask_intent_default(self, msg: str):
        assert classify_intent(msg) == "ask"

    # ── Priority order ─────────────────────────────────────────────────────
    def test_quiz_has_higher_priority_than_ask(self):
        # "quiz" keyword should override default "ask"
        assert classify_intent("Generate quiz questions about photosynthesis") == "quiz"

    def test_returns_string(self):
        result = classify_intent("any message")
        assert isinstance(result, str)

    def test_all_valid_intents(self):
        valid = {"ask", "quiz", "summary", "flashcard", "teach"}
        for msg in ["what?", "quiz me", "summarize", "flashcard", "explain simply"]:
            assert classify_intent(msg) in valid

    def test_intent_description(self):
        desc = get_intent_description("quiz")
        assert "quiz" in desc.lower() or "Quiz" in desc
