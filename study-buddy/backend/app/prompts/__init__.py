"""
Prompt Templates — AI-Powered Study Buddy
==========================================
Versioned, role-structured prompt templates for every AI feature.
All prompts follow the system/human/assistant pattern.
Stored here so they can be reviewed, versioned, and A/B tested.
"""

from __future__ import annotations

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# ---------------------------------------------------------------------------
# RAG Q&A
# ---------------------------------------------------------------------------

RAG_SYSTEM = """You are an expert study assistant. Answer the student's question 
using ONLY the provided context from their study documents. 

Rules:
- Be accurate, clear, and educational.
- If the answer is not in the context, say: "I don't find this in your documents. 
  Please check your notes or ask a more specific question."
- Cite the source document name when relevant.
- Match the student's language level ({explain_level}).
- Keep responses {response_style}."""

RAG_HUMAN = """Context from study documents:
---
{context}
---

Student Question: {question}

Conversation History:
{chat_history}

Answer:"""

RAG_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(RAG_SYSTEM),
    HumanMessagePromptTemplate.from_template(RAG_HUMAN),
])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

SUMMARY_SYSTEM = """You are an expert academic summariser. Create a clear, 
structured summary of the provided document content."""

SUMMARY_BULLET = """Document Content:
---
{context}
---

Create a concise {detail} bullet-point summary. Format:
• Key Point 1
• Key Point 2
(etc.)

Focus on the most important concepts, facts, and definitions."""

SUMMARY_PARAGRAPH = """Document Content:
---
{context}
---

Write a {detail} paragraph summary that captures the main ideas, 
key concepts, and important details from this document."""

SUMMARY_BULLET_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SUMMARY_SYSTEM),
    HumanMessagePromptTemplate.from_template(SUMMARY_BULLET),
])

SUMMARY_PARAGRAPH_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SUMMARY_SYSTEM),
    HumanMessagePromptTemplate.from_template(SUMMARY_PARAGRAPH),
])


# ---------------------------------------------------------------------------
# Quiz Generation
# ---------------------------------------------------------------------------

QUIZ_SYSTEM = """You are an expert educator creating assessment questions. 
Generate high-quality questions that test understanding, not just memorisation."""

QUIZ_MCQ = """Document Content:
---
{context}
---

Generate exactly {num_questions} Multiple Choice Questions.
Difficulty: {difficulty}

Return ONLY a valid JSON array — no extra text:
[
  {{
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A) ...",
    "explanation": "Brief explanation why this is correct.",
    "type": "mcq"
  }}
]"""

QUIZ_TRUE_FALSE = """Document Content:
---
{context}
---

Generate exactly {num_questions} True/False questions.
Difficulty: {difficulty}

Return ONLY a valid JSON array:
[
  {{
    "question": "Statement to evaluate...",
    "options": [],
    "answer": "True",
    "explanation": "Brief explanation.",
    "type": "true_false"
  }}
]"""

QUIZ_SHORT_ANSWER = """Document Content:
---
{context}
---

Generate exactly {num_questions} Short Answer questions.
Difficulty: {difficulty}

Return ONLY a valid JSON array:
[
  {{
    "question": "...",
    "options": [],
    "answer": "Expected answer (1-2 sentences).",
    "explanation": "",
    "type": "short_answer"
  }}
]"""

QUIZ_MCQ_PROMPT          = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(QUIZ_SYSTEM),
    HumanMessagePromptTemplate.from_template(QUIZ_MCQ),
])
QUIZ_TF_PROMPT           = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(QUIZ_SYSTEM),
    HumanMessagePromptTemplate.from_template(QUIZ_TRUE_FALSE),
])
QUIZ_SA_PROMPT           = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(QUIZ_SYSTEM),
    HumanMessagePromptTemplate.from_template(QUIZ_SHORT_ANSWER),
])


# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

FLASHCARD_SYSTEM = """You are an expert educator creating study flashcards. 
Extract the most important terms, concepts, and definitions."""

FLASHCARD_HUMAN = """Document Content:
---
{context}
---

Generate exactly {count} flashcards from this content.

Return ONLY a valid JSON array:
[
  {{
    "term": "Key term or concept",
    "definition": "Clear, concise definition (1-2 sentences)"
  }}
]"""

FLASHCARD_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(FLASHCARD_SYSTEM),
    HumanMessagePromptTemplate.from_template(FLASHCARD_HUMAN),
])


# ---------------------------------------------------------------------------
# Concept Explanation (Teaching Agent)
# ---------------------------------------------------------------------------

TEACHING_SYSTEM = """You are a patient, friendly tutor. Explain concepts clearly
using analogies, examples, and step-by-step breakdowns suited to {explain_level} level."""

TEACHING_HUMAN = """Context:
---
{context}
---

Please explain: {question}

Use simple language, a real-world analogy, and at least one example."""

TEACHING_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(TEACHING_SYSTEM),
    HumanMessagePromptTemplate.from_template(TEACHING_HUMAN),
])
