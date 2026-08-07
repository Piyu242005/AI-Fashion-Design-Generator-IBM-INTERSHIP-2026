# Quiz API

**Base URL:** `http://localhost:8000`  
**Authentication:** All endpoints require `Authorization: Bearer <token>`

---

## POST `/api/v1/quiz/generate`

Generate quiz questions from a document using Google Gemini via the QuizAgent.

### Request Body

```json
{
  "document_id": 1,
  "num_questions": 5,
  "question_type": "mcq",
  "difficulty": "medium",
  "topic": "Photosynthesis"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `document_id` | int | ✅ | — | ID of the document to generate from |
| `num_questions` | int | ✅ | — | Number of questions (3–20) |
| `question_type` | string | ✅ | — | `mcq` \| `true_false` \| `short_answer` \| `mixed` |
| `difficulty` | string | ✅ | — | `easy` \| `medium` \| `hard` |
| `topic` | string | ❌ | All topics | Filter to a specific topic/chapter |

### Response `200 OK`

```json
{
  "document_id": 1,
  "questions": [
    {
      "question": "What is the primary pigment used in photosynthesis?",
      "options": ["Chlorophyll", "Melanin", "Carotene", "Hemoglobin"],
      "answer": "Chlorophyll",
      "explanation": "Chlorophyll is the green pigment in chloroplasts that absorbs light energy to drive the light-dependent reactions of photosynthesis.",
      "type": "mcq"
    },
    {
      "question": "Photosynthesis only occurs during daylight hours.",
      "options": ["True", "False"],
      "answer": "True",
      "explanation": "The light-dependent reactions require sunlight. Only the Calvin cycle (light-independent) can technically occur in the dark.",
      "type": "true_false"
    },
    {
      "question": "Name the two main stages of photosynthesis.",
      "options": [],
      "answer": "Light-dependent reactions and the Calvin cycle (light-independent reactions)",
      "explanation": "The two main stages are: (1) light-dependent reactions in the thylakoid membrane producing ATP and NADPH, and (2) the Calvin cycle in the stroma using those products to fix CO₂ into glucose.",
      "type": "short_answer"
    }
  ],
  "num_questions": 5,
  "question_type": "mixed",
  "difficulty": "medium"
}
```

### Question Type Details

| Type | `options` | How graded |
|---|---|---|
| `mcq` | 4 options array | Exact match to `answer` string |
| `true_false` | `["True", "False"]` | Exact match |
| `short_answer` | Empty array `[]` | Case-insensitive partial match |
| `mixed` | Varies | Mixed of all above |

### Errors

| Code | Description |
|---|---|
| `401` | Unauthorized |
| `404` | Document not found or not owned by user |
| `503` | Gemini API unavailable |

---

## POST `/api/v1/quiz/submit`

Submit quiz results to persist the score and update topic performance tracking.

### Request Body

```json
{
  "document_id": 1,
  "topic": "Photosynthesis",
  "score_pct": 80.0,
  "num_questions": 5,
  "question_type": "mcq"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `document_id` | int | ✅ | Document the quiz was generated from |
| `topic` | string | ✅ | Topic name (used for dashboard grouping) |
| `score_pct` | float | ✅ | Score as percentage 0.0–100.0 |
| `num_questions` | int | ✅ | Total questions attempted |
| `question_type` | string | ✅ | Type of quiz taken |

### Response `200 OK`

```json
{
  "message": "Quiz result saved.",
  "score_pct": 80.0,
  "topic_avg": 75.5,
  "total_attempts": 3
}
```

### Side Effects

Submitting a quiz result:
1. Creates a `quiz_results` record in the database
2. Updates (or creates) the `topic_scores` record with a rolling average
3. The updated topic score is reflected immediately on the Dashboard
4. The RecommendationEngine uses topic scores to generate personalised study advice

### Errors

| Code | Description |
|---|---|
| `401` | Unauthorized |
| `422` | Invalid score value (must be 0.0–100.0) |
