"""
Constants — AI-Powered Study Buddy
=====================================
Application-wide constant values.
Keep magic numbers out of business logic by naming them here.
"""

# File processing
SUPPORTED_MIME_TYPES: dict[str, str] = {
    "application/pdf":                                             "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "text/plain":                                                  "txt",
}

# Embedding
EMBEDDING_DIMENSION = 384          # all-MiniLM-L6-v2 output size

# RAG
MIN_CHUNK_CHARS = 100              # discard tiny chunks
MAX_CONTEXT_CHARS = 8000           # max chars sent to LLM as context

# Quiz
QUIZ_MIN_QUESTIONS = 3
QUIZ_MAX_QUESTIONS = 15
QUIZ_DEFAULT_COUNT = 5

# Flashcards
FLASHCARD_MIN = 3
FLASHCARD_MAX = 30
FLASHCARD_DEFAULT = 10

# Study streak
STREAK_WINDOW_HOURS = 24

# API
API_V1_PREFIX = "/api/v1"

# Quiz difficulty → prompt instruction mapping
QUIZ_DIFFICULTY_MAP: dict[str, str] = {
    "easy":   "Use simple vocabulary and straightforward questions suitable for beginners.",
    "medium": "Use standard academic language. Mix recall and comprehension questions.",
    "hard":   "Use complex, analytical questions that require deep understanding of the material.",
}
