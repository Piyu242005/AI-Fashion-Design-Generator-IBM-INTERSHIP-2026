# Quiz API

Base URL: `http://localhost:8000`
All endpoints require `Authorization: Bearer <token>`.

---

## POST /quiz/generate

Generate quiz questions from a document using Gemini.

**Request Body**
```json
{
  "document_id": 1,
  "num_questions": 5,
  "question_type": "mcq",
  "difficulty": "medium",
  "topic": "Photosynthesis"
}
```

`question_type` options: `mcq` | `true_false` | `short_answer` | `mixed`  
`difficulty` options: `easy` | `medium` | `hard`

**Response** `200 OK`
```json
{
  "document_id": 1,
  "questions": [
    {
      "question": "What is the primary pigment used in photosynthesis?",
      "options": ["Chlorophyll", "Melanin", "Carotene", "Hemoglobin"],
      "answer": "Chlorophyll",
      "explanation": "Chlorophyll absorbs light energy to drive photosynthesis.",
      "type": "mcq"
    }
  ],
  "num_questions": 5,
  "question_type": "mcq",
  "difficulty": "medium"
}
```

---

## POST /quiz/submit

Submit quiz results and update topic scores.

**Request Body**
```json
{
  "document_id": 1,
  "topic": "Photosynthesis",
  "score_pct": 80.0,
  "num_questions": 5
}
```

**Response** `200 OK`
```json
{
  "message": "Result saved.",
  "score_pct": 80.0
}
```
