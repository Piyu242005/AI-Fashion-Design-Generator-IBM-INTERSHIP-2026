# Chat (RAG) API

Base URL: `http://localhost:8000`
All endpoints require `Authorization: Bearer <token>`.

---

## POST /chat/

Ask a question about your uploaded documents (RAG pipeline).

**Request Body**
```json
{
  "question": "What is photosynthesis?",
  "document_ids": [1, 2]
}
```

**Response** `200 OK`
```json
{
  "answer": "Photosynthesis is the process by which plants convert sunlight...",
  "sources": ["biology_notes.pdf"],
  "intent": "ask",
  "latency_ms": 1243
}
```

**Errors**
- `401` — Unauthorized
- `422` — Validation error

---

## DELETE /chat/history

Clear the current user's chat history.

**Response** `200 OK`
```json
{
  "message": "Chat history cleared."
}
```
