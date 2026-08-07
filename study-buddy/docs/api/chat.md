# Chat (RAG) API

**Base URL:** `http://localhost:8000`  
**Authentication:** All endpoints require `Authorization: Bearer <token>`

---

## POST `/api/v1/chat/`

Ask a question about your uploaded documents using the RAG pipeline.

The request is routed through the **AgentRouter** which classifies the intent
and dispatches to the correct specialised agent (RAG, Quiz, Summary, Flashcard, Teaching).

### Request Body

```json
{
  "question": "What is photosynthesis?",
  "document_ids": [1, 2]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | ✅ | Natural language question |
| `document_ids` | int[] | ✅ | List of document IDs to search (scope) |

### Response `200 OK`

```json
{
  "answer": "Photosynthesis is the process by which plants use sunlight, water and CO₂ to produce glucose and oxygen. According to your notes, it occurs in the chloroplasts...",
  "sources": ["biology_notes.pdf"],
  "intent": "ask",
  "intent_label": "Document Q&A",
  "agent_name": "RAGAgent",
  "latency_ms": 1243
}
```

| Field | Type | Description |
|---|---|---|
| `answer` | string | AI-generated answer grounded in documents |
| `sources` | string[] | Filenames of documents used in the answer |
| `intent` | string | Classified intent: `ask`, `quiz`, `summary`, `flashcard`, `teach`, `blocked` |
| `intent_label` | string | Human-readable intent label |
| `agent_name` | string | Agent that handled the request |
| `latency_ms` | int | Total processing time in milliseconds |

### Intent Routing

The same `/chat/` endpoint handles all intents:

| User says... | Intent | Agent | Action |
|---|---|---|---|
| "What is...?" / "Explain..." | `ask` | RAGAgent | Document Q&A with sources |
| "Generate a quiz..." | `quiz` | QuizAgent | Redirect to quiz page |
| "Summarise..." | `summary` | SummaryAgent | Return summary inline |
| "Create flashcards..." | `flashcard` | FlashcardAgent | Redirect to flashcards |
| "Teach me..." | `teach` | TeachingAgent | Plain-language explanation |

### Errors

| Code | Description |
|---|---|
| `400` | Input blocked by guardrails (injection, PII, toxicity) |
| `401` | Missing or invalid JWT token |
| `404` | One or more document_ids not found |
| `422` | Validation error (empty question, etc.) |
| `503` | Google Gemini API unavailable |

---

## GET `/api/v1/chat/history`

Retrieve the authenticated user's chat history (last 50 messages).

### Response `200 OK`

```json
[
  {
    "id": 42,
    "question": "What is photosynthesis?",
    "answer": "Photosynthesis is...",
    "sources": ["biology_notes.pdf"],
    "intent": "ask",
    "created_at": "2025-08-07T14:32:00Z"
  }
]
```

---

## DELETE `/api/v1/chat/history`

Clear all chat history for the authenticated user.

### Response `200 OK`

```json
{
  "message": "Chat history cleared."
}
```

---

## Guardrails

Every chat request passes through the following safety checks before reaching the AI:

1. **Prompt Injection** — Detects `ignore previous instructions`, `system:`, `<|im_start|>` patterns
2. **PII Detection** — Flags email addresses, phone numbers, SSNs in the input
3. **Toxicity Filter** — Blocks hate speech, threats, and explicit content keywords
4. **Length Validation** — Rejects questions shorter than 3 or longer than 2,000 characters
5. **Output Validation** — Checks the generated response for quality before returning

Blocked requests return `400` with a descriptive error message.
