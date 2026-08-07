# Flashcards API

**Base URL:** `http://localhost:8000`  
**Authentication:** All endpoints require `Authorization: Bearer <token>`

---

## POST `/api/v1/flashcards/generate`

Generate study flashcards from a document using the FlashcardAgent.

The agent retrieves key-term-rich chunks from ChromaDB and uses a structured
Gemini prompt to extract term → definition pairs in valid JSON format.

### Request Body

```json
{
  "document_id": 1,
  "num_cards": 10
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `document_id` | int | ✅ | — | ID of the document to generate from |
| `num_cards` | int | ❌ | `10` | Number of flashcards (5–30) |

### Response `200 OK`

```json
{
  "document_id": 1,
  "filename": "biology_notes.pdf",
  "flashcards": [
    {
      "front": "What is photosynthesis?",
      "back": "The process by which plants use sunlight, water and CO₂ to produce glucose (C₆H₁₂O₆) and oxygen (O₂). Occurs in the chloroplasts."
    },
    {
      "front": "What is chlorophyll?",
      "back": "The green pigment found in chloroplasts that captures light energy (primarily red and blue wavelengths) to drive the light-dependent reactions of photosynthesis."
    },
    {
      "front": "What are the two main stages of photosynthesis?",
      "back": "1. Light-dependent reactions (in the thylakoid membrane): produce ATP and NADPH.\n2. Calvin cycle / Light-independent reactions (in the stroma): use ATP and NADPH to fix CO₂ into glucose."
    },
    {
      "front": "Define the Calvin Cycle.",
      "back": "A series of biochemical reactions in the stroma of chloroplasts that fix atmospheric CO₂ into organic molecules (G3P) using the ATP and NADPH produced by the light-dependent reactions. Also called the light-independent reactions."
    }
  ],
  "num_cards": 10,
  "generated_count": 10
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `document_id` | int | Source document ID |
| `filename` | string | Original document filename |
| `flashcards` | Flashcard[] | Array of term-definition pairs |
| `flashcards[].front` | string | Question / term (front of card) |
| `flashcards[].back` | string | Answer / definition (back of card) |
| `num_cards` | int | Requested number of cards |
| `generated_count` | int | Actual number generated (may be less if document is short) |

### How Flashcards Are Generated

```
1. Embed a "key terms and definitions" query
2. Retrieve 15 most term-rich chunks from ChromaDB
3. Build structured prompt: "Extract {N} key term-definition pairs as JSON"
4. Gemini generates JSON array of {front, back} objects
5. JSON parser validates and extracts pairs
6. Return as FlashcardResponse
```

### Usage Recommendations

| Document Type | Recommended `num_cards` |
|---|---|
| Short (1–5 pages) | 5–10 |
| Medium (5–20 pages) | 10–20 |
| Long (20+ pages) | 20–30 |
| Glossary/Vocabulary | 20–30 |

### Errors

| Code | Description |
|---|---|
| `401` | Unauthorized |
| `404` | Document not found or not owned by user |
| `422` | `num_cards` must be between 1 and 50 |
| `503` | Gemini API unavailable |

---

## Study Flow Integration

Flashcards work best as part of this study workflow:

```
1. Upload document           → /api/v1/documents/upload
2. Get overview              → /api/v1/summary/
3. Generate flashcards       → /api/v1/flashcards/generate
4. Study cards (Known/Review)→ Frontend flip card UI
5. Take a quiz               → /api/v1/quiz/generate
6. Check weak topics         → /api/v1/dashboard/
7. Chat for clarification    → /api/v1/chat/
```

This sequence follows the **Spaced Repetition** + **Active Recall** learning strategy
proven to improve long-term memory retention.
