# Summary API

**Base URL:** `http://localhost:8000`  
**Authentication:** All endpoints require `Authorization: Bearer <token>`

---

## POST `/api/v1/summary/`

Generate an AI-powered summary of a document using the SummaryAgent.

The agent retrieves the most representative chunks from ChromaDB and condenses
them into the requested format using a structured Gemini prompt.

### Request Body

```json
{
  "document_id": 1,
  "style": "bullet",
  "detail": "standard"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `document_id` | int | ✅ | — | ID of document to summarise |
| `style` | string | ✅ | — | `bullet` \| `paragraph` \| `detailed` |
| `detail` | string | ❌ | `standard` | `brief` \| `standard` \| `comprehensive` |

### Style Options

| Style | Description | Typical length |
|---|---|---|
| `bullet` | Numbered bullet points covering key ideas | 150–300 words |
| `paragraph` | Flowing prose summary | 200–400 words |
| `detailed` | Extended summary with section headers | 400–800 words |

### Detail Level Options

| Detail | Description |
|---|---|
| `brief` | Top 3–5 key points only |
| `standard` | Balanced coverage of all major topics |
| `comprehensive` | In-depth summary including examples and implications |

### Response `200 OK`

#### Bullet style example

```json
{
  "document_id": 1,
  "filename": "biology_notes.pdf",
  "summary": "**Key Points from Biology Notes:**\n\n1. **Photosynthesis** is the process by which plants convert light energy into chemical energy (glucose)\n2. **Two main stages:** Light-dependent reactions (thylakoid membrane) and Calvin cycle (stroma)\n3. **Reactants:** CO₂ + H₂O + Light energy\n4. **Products:** Glucose (C₆H₁₂O₆) + O₂\n5. **Chlorophyll** is the primary photosynthetic pigment, absorbing red and blue light\n6. **C3, C4, and CAM plants** use different strategies to adapt photosynthesis to their environments",
  "style": "bullet",
  "detail": "standard",
  "word_count": 87
}
```

#### Paragraph style example

```json
{
  "document_id": 1,
  "filename": "biology_notes.pdf",
  "summary": "This document provides a comprehensive overview of photosynthesis, the fundamental biological process by which plants, algae, and some bacteria convert light energy into chemical energy stored as glucose...",
  "style": "paragraph",
  "detail": "standard",
  "word_count": 234
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `document_id` | int | Source document ID |
| `filename` | string | Original filename |
| `summary` | string | Generated summary (Markdown formatted) |
| `style` | string | Style used |
| `detail` | string | Detail level used |
| `word_count` | int | Approximate word count of the summary |

### Errors

| Code | Description |
|---|---|
| `401` | Unauthorized |
| `404` | Document not found or document has no processed chunks |
| `503` | Gemini API unavailable |

---

## Notes

- Summaries are generated fresh on each request (not cached) to allow different style/detail combinations.
- The summary is grounded in the document's actual content via ChromaDB retrieval — it will not add information not present in your document.
- Markdown formatting is intentional — both the Streamlit and Next.js frontends render Markdown.
