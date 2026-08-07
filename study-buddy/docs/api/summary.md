# Summary API

Base URL: `http://localhost:8000`
All endpoints require `Authorization: Bearer <token>`.

---

## POST /summary/generate

Generate an AI summary of a document.

**Request Body**
```json
{
  "document_id": 1,
  "style": "concise"
}
```

`style` options: `concise` | `detailed` | `bullet_points`

**Response** `200 OK`
```json
{
  "document_id": 1,
  "filename": "biology_notes.pdf",
  "summary": "This document covers the fundamentals of photosynthesis...",
  "style": "concise",
  "word_count": 150
}
```
