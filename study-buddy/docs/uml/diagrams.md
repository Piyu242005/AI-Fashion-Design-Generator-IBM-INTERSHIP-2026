# UML Diagrams — AI-Powered Study Buddy

This directory contains all UML and system diagrams for the project.

---

## 1. Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI-POWERED STUDY BUDDY                        │
│                                                                       │
│   ┌──────────┐                                                        │
│   │          │──────────── Register / Login ──────────────►         │
│   │          │                                                        │
│   │          │──────────── Upload Document ────────────────►         │
│   │          │                                                        │
│   │ STUDENT  │──────────── Ask Question (RAG) ─────────────►         │
│   │          │                                                        │
│   │          │──────────── Generate Quiz ──────────────────►         │
│   │          │                                                        │
│   │          │──────────── Generate Flashcards ────────────►         │
│   │          │                                                        │
│   │          │──────────── Summarise Document ─────────────►         │
│   │          │                                                        │
│   │          │──────────── Explain Concept ────────────────►         │
│   │          │                                                        │
│   │          │──────────── View Dashboard ─────────────────►         │
│   │          │                                                        │
│   └──────────┘──────────── Get Recommendations ────────────►         │
│                                                                       │
│   ┌────────────┐                                                      │
│   │            │──────────── Process Document ───────────────►       │
│   │  SYSTEM    │──────────── Store Embeddings ────────────────►      │
│   │  (Backend) │──────────── Retrieve Context ───────────────►       │
│   │            │──────────── Invoke Gemini API ──────────────►       │
│   └────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Class Diagram — Backend Core

```
┌──────────────────────┐       ┌──────────────────────┐
│       User           │       │      Document         │
├──────────────────────┤       ├──────────────────────┤
│ + id: int            │  1──* │ + id: int             │
│ + name: str          │       │ + user_id: int (FK)   │
│ + email: str         │       │ + filename: str       │
│ + hashed_password: str│      │ + file_type: str      │
│ + is_active: bool    │       │ + chunk_count: int    │
│ + study_streak: int  │       │ + chroma_ids: list    │
│ + created_at: datetime│      │ + status: str         │
└──────────────────────┘       └──────────────────────┘
          │                                │
          │ 1                              │ 1
          │ *                              │ *
┌──────────────────────┐       ┌──────────────────────┐
│    ChatHistory       │       │    QuizResult         │
├──────────────────────┤       ├──────────────────────┤
│ + id: int            │       │ + id: int             │
│ + user_id: int (FK)  │       │ + user_id: int (FK)   │
│ + doc_id: int (FK)   │       │ + doc_id: int (FK)    │
│ + question: str      │       │ + topic: str          │
│ + answer: str        │       │ + score_pct: float    │
│ + sources: JSON      │       │ + num_questions: int  │
│ + intent: str        │       │ + question_type: str  │
│ + created_at: datetime│      │ + created_at: datetime│
└──────────────────────┘       └──────────────────────┘


┌──────────────────────┐       ┌──────────────────────┐
│    AgentRouter       │       │  IntentClassifier    │
├──────────────────────┤       ├──────────────────────┤
│ - _rag: RAGAgent     │──────►│ + classify(): str    │
│ - _quiz: QuizAgent   │       │                      │
│ - _summary: Summary  │       │  Intent values:      │
│ - _flashcard: Flash  │       │  ask / quiz /        │
│ - _teaching: Teach   │       │  summary /           │
├──────────────────────┤       │  flashcard / teach   │
│ + route(): dict      │       └──────────────────────┘
└──────────────────────┘
          │
          ├──► RAGAgent.run()
          ├──► QuizAgent.run()
          ├──► SummaryAgent.run()
          ├──► FlashcardAgent.run()
          └──► TeachingAgent.run()
                    │
                    ▼
            VectorStoreService
            (ChromaDB queries)
                    │
                    ▼
            GeminiClient (LLM)
```

---

## 3. Sequence Diagram — RAG Q&A Flow

```
Student     Frontend     FastAPI      AgentRouter   VectorStore    Gemini
   │            │            │             │              │            │
   │──question─►│            │             │              │            │
   │            │──POST /chat►│             │              │            │
   │            │            │─validate JWT │              │            │
   │            │            │─guardrails──►│              │            │
   │            │            │─classify────►│              │            │
   │            │            │             │──embed query──►│            │
   │            │            │             │              │──similarity  │
   │            │            │             │◄──top-K chunks│            │
   │            │            │             │──build prompt─────────────►│
   │            │            │             │◄──generated answer─────────│
   │            │            │─validate output             │            │
   │            │◄──response──│             │              │            │
   │◄──answer───│            │             │              │            │
```

---

## 4. Entity-Relationship (ER) Diagram

```
┌───────────┐         ┌─────────────┐         ┌──────────────┐
│   users   │         │  documents  │         │ chat_history │
├───────────┤         ├─────────────┤         ├──────────────┤
│ PK id     │──┐      │ PK id       │──┐      │ PK id        │
│ name      │  │ 1:N  │ FK user_id  │◄─┘      │ FK user_id   │
│ email     │  └─────►│ filename    │  │ 1:N  │ FK document_id│
│ hashed_pw │         │ file_type   │  └─────►│ question     │
│ is_active │         │ chunk_count │         │ answer       │
│ streak    │         │ status      │         │ sources JSON │
│ created_at│         │ uploaded_at │         │ intent       │
└───────────┘         └─────────────┘         │ created_at   │
     │                                         └──────────────┘
     │ 1:N
     ▼
┌──────────────┐         ┌──────────────┐
│ quiz_results │         │ topic_scores │
├──────────────┤         ├──────────────┤
│ PK id        │         │ PK id        │
│ FK user_id   │         │ FK user_id   │
│ FK doc_id    │         │ topic        │
│ topic        │         │ avg_score    │
│ score_pct    │         │ attempts     │
│ num_questions│         │ updated_at   │
│ question_type│         └──────────────┘
│ created_at   │
└──────────────┘
```

---

## 5. Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└──────┬────────────────────────────┬───────────────────────────┘
       │                            │
       ▼                            ▼
┌────────────────┐         ┌────────────────┐
│ Streamlit Cloud│         │  Vercel / CDN  │
│ (IBM Version)  │         │  (Next.js v2)  │
│                │         │                │
│ Port 8501      │         │ Port 443       │
└───────┬────────┘         └───────┬────────┘
        │                          │
        │ HTTPS REST API           │ HTTPS REST API
        │                          │
        └────────────┬─────────────┘
                     │
                     ▼
           ┌─────────────────┐
           │   Render.com    │
           │  FastAPI Backend│
           │   Port 8000     │
           ├─────────────────┤
           │  SQLite DB      │
           │  ChromaDB       │
           │  ./uploads/     │
           └────────┬────────┘
                    │ API calls
                    ▼
           ┌─────────────────┐
           │  Google Gemini  │
           │   1.5 Pro API   │
           └─────────────────┘
```

---

## 6. AI Agent Architecture Diagram

```
User Input
    │
    ▼
┌─────────────────────────────┐
│       Guardrails Layer       │  ← Prompt injection check
│  validate_input(message)     │  ← PII detection
│                             │  ← Toxicity filter
└──────────────┬──────────────┘  ← Length validation
               │ safe_message
               ▼
┌─────────────────────────────┐
│     IntentClassifier         │
│  keyword + regex matching    │
└──────────────┬──────────────┘
               │ intent
               ▼
┌──────────────────────────────────────────────────┐
│                   AgentRouter                     │
│                                                   │
│  "ask"       ──► RAGAgent                         │
│  "quiz"      ──► QuizAgent                        │
│  "summary"   ──► SummaryAgent                     │
│  "flashcard" ──► FlashcardAgent                   │
│  "teach"     ──► TeachingAgent                    │
└──────────────────────────────────────────────────┘
               │ agent.run()
               ▼
┌─────────────────────────────┐
│    LangChain LCEL Chain      │
│  prompt | llm | parser       │
└──────────────┬──────────────┘
               │ chain.invoke()
               ├──► VectorStoreService (ChromaDB)
               │         │
               │         └──► Sentence Transformer embed
               │         └──► Cosine similarity search
               │         └──► Top-K chunks returned
               │
               └──► GeminiClient (google-generativeai)
                         │
                         └──► gemini-1.5-pro generate()
               │
               ▼
┌─────────────────────────────┐
│     Guardrails Layer         │
│  validate_output(response)   │  ← Hallucination check
└──────────────┬──────────────┘  ← Source citation add
               │
               ▼
         Final Response → User
```
