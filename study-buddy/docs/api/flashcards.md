# Flashcards API

Base URL: `http://localhost:8000`
All endpoints require `Authorization: Bearer <token>`.

---

## POST /flashcards/generate

Generate flashcards from a document using Gemini.

**Request Body**
```json
{
  "document_id": 1,
  "num_cards": 10
}
```

**Response** `200 OK`
```json
{
  "document_id": 1,
  "flashcards": [
    {
      "front": "What is photosynthesis?",
      "back": "The process by which plants use sunlight, water and CO2 to produce glucose and oxygen."
    }
  ],
  "num_cards": 10
}
```
