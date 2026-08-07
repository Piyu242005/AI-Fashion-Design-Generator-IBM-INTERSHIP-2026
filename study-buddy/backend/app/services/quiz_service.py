"""
Quiz Service — AI-Powered Study Buddy
========================================
Generates AI quizzes and saves submitted results.
Supports MCQ, True/False, Short Answer, and Mixed types.
"""

from __future__ import annotations

import json
import logging
import re

from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import get_gemini_llm, invoke_with_retry
from app.ai.vector_store import VectorStoreService
from app.core.constants import QUIZ_DIFFICULTY_MAP
from app.exceptions import NotFoundError
from app.guardrails import validate_output
from app.prompts import QUIZ_MCQ_PROMPT, QUIZ_TF_PROMPT, QUIZ_SA_PROMPT
from app.repositories.document_repo import DocumentRepository
from app.repositories.session_repo import SessionRepository
from app.schemas import (
    QuizRequest, QuizResponse, QuizQuestion,
    QuizSubmitRequest,
)

logger = logging.getLogger("study_buddy.quiz_service")

_PROMPT_MAP = {
    "mcq":          QUIZ_MCQ_PROMPT,
    "true_false":   QUIZ_TF_PROMPT,
    "short_answer": QUIZ_SA_PROMPT,
}


class QuizService:
    def __init__(self, db: AsyncSession) -> None:
        self._doc_repo  = DocumentRepository(db)
        self._sess_repo = SessionRepository(db)
        self._vs        = VectorStoreService()

    async def generate(self, user_id: int, req: QuizRequest) -> QuizResponse:
        """Generate quiz questions from a document using Gemini."""

        # Validate document ownership
        doc = await self._doc_repo.get_by_id(req.document_id)
        if not doc or doc.user_id != user_id:
            raise NotFoundError("Document")

        # Retrieve relevant chunks (use doc title as query for broad coverage)
        chunks = self._vs.query(
            question=f"main topics and key concepts from {doc.filename}",
            user_id=user_id,
            doc_ids=[req.document_id],
            top_k=8,
        )
        if not chunks:
            raise ValueError("No content found in this document for quiz generation.")

        context = "\n\n".join(c["content"] for c in chunks)[:6000]
        difficulty_instruction = QUIZ_DIFFICULTY_MAP.get(req.difficulty, QUIZ_DIFFICULTY_MAP["medium"])

        # Handle mixed type: split between MCQ and T/F
        if req.question_type == "mixed":
            half   = req.num_questions // 2
            rest   = req.num_questions - half
            mcq_q  = await self._generate_type(context, "mcq",         half, difficulty_instruction)
            tf_q   = await self._generate_type(context, "true_false",  rest, difficulty_instruction)
            questions = mcq_q + tf_q
        else:
            questions = await self._generate_type(
                context, req.question_type, req.num_questions, difficulty_instruction
            )

        return QuizResponse(
            document_id=req.document_id,
            questions=questions,
            num_questions=len(questions),
            question_type=req.question_type,
            difficulty=req.difficulty,
        )

    async def _generate_type(
        self,
        context: str,
        qtype: str,
        count: int,
        difficulty: str,
    ) -> list[QuizQuestion]:
        """Generate questions of a single type."""
        prompt = _PROMPT_MAP.get(qtype, QUIZ_MCQ_PROMPT)
        llm    = get_gemini_llm()
        chain  = prompt | llm | StrOutputParser()

        raw = invoke_with_retry(chain, {
            "context":       context,
            "num_questions": count,
            "difficulty":    difficulty,
        })

        validated = validate_output(raw)
        return _parse_questions(validated, qtype)

    async def submit_result(self, user_id: int, req: QuizSubmitRequest) -> dict:
        """Save quiz result and update topic scores."""
        await self._sess_repo.save_quiz_result(
            user_id=user_id,
            document_id=req.document_id,
            topic=req.topic,
            score_pct=req.score_pct,
            num_questions=req.num_questions,
            question_type="mcq",
        )
        await self._sess_repo.upsert_topic_score(
            user_id=user_id,
            topic=req.topic,
            new_score=req.score_pct,
        )
        logger.info(
            "Quiz result saved: user=%d topic=%s score=%.1f%%",
            user_id, req.topic, req.score_pct,
        )
        return {"message": "Result saved.", "score_pct": req.score_pct}


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _parse_questions(raw: str, qtype: str) -> list[QuizQuestion]:
    """Extract JSON array from LLM response and parse into QuizQuestion objects."""
    # Strip markdown code fences if present
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    # Find the JSON array
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if not match:
        logger.warning("No JSON array found in quiz response: %s", raw[:200])
        return []
    try:
        items = json.loads(match.group(0))
        return [
            QuizQuestion(
                question=item.get("question", ""),
                options=item.get("options", []),
                answer=item.get("answer", ""),
                explanation=item.get("explanation", ""),
                type=item.get("type", qtype),
            )
            for item in items
            if item.get("question")
        ]
    except json.JSONDecodeError as e:
        logger.error("JSON parse error in quiz response: %s", e)
        return []
