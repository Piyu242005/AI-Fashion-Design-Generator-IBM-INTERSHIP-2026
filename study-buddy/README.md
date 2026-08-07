# 🎓 AI-Powered Study Buddy

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=flat)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Pro-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange?style=flat)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![IBM SkillsBuild](https://img.shields.io/badge/IBM-SkillsBuild_2025-054ADA?style=flat&logo=ibm&logoColor=white)](https://skillsbuild.org)

> **A production-grade Generative AI study assistant** that lets students upload documents (PDF, DOCX, PPTX, TXT), ask questions, receive grounded answers via RAG, generate quizzes and flashcards, summarise notes, and get personalised AI study recommendations — all powered by Google Gemini 1.5 Pro, LangChain, and ChromaDB.

---

## 🌟 Features

- **📄 Multi-format Upload** — PDF, DOCX, PPTX, TXT up to 50 MB
- **🔍 RAG-Powered Q&A** — Answers grounded in your own documents via ChromaDB semantic search
- **📝 Smart Summaries** — Bullet-point or paragraph summaries at configurable detail levels
- **❓ Quiz Generator** — MCQ, True/False, Short Answer, and Mixed quizzes with difficulty control
- **🃏 Flashcards** — Auto-generated term→definition flip cards with Known/Review tracking
- **💡 Concept Explainer** — Plain-language explanations with analogies adapted to your level
- **🤖 AI Agent Architecture** — Intent classifier routes to 5 specialised agents (RAG, Quiz, Summary, Flashcard, Teaching)
- **🧠 5 Memory Types** — Session, conversation, preference, study history, weak topic memory
- **📊 Smart Dashboard** — KPI cards, topic progress bars, AI recommendations, activity feed
- **🔥 Study Streak** — Daily streak tracking to build consistent study habits
- **🛡️ AI Guardrails** — Prompt injection protection, PII detection, toxicity filtering, hallucination reduction
- **🎨 5 Themes** — Dark, Light, Blue, Purple, System — switchable live

---

## 🏗️ Architecture

**One backend. Two frontends.** The FastAPI backend serves both the Streamlit IBM version
and the Next.js portfolio version without any changes.

```
     ┌──────────────────────┐      ┌──────────────────────┐
     │  Streamlit Frontend  │      │   Next.js Frontend   │
     │  (IBM SkillsBuild)   │      │  (Portfolio Edition) │
     │  frontend-streamlit/ │      │   frontend-web/      │
     │     Port 8501        │      │     Port 3000        │
     └──────────┬───────────┘      └──────────┬───────────┘
                │                             │
                └────────────┬────────────────┘
                             │  HTTPS REST API
                             ▼
     ┌───────────────────────────────────────────────────┐
     │  API GATEWAY  —  FastAPI 0.111 + JWT + CORS        │
     │  15 endpoints · Validation · Request-ID Logging   │
     ├───────────────────────────────────────────────────┤
     │  BUSINESS LOGIC  —  Services + AgentRouter         │
     │  RAG · Quiz · Summary · Flashcard · Dashboard      │
     ├───────────────────────────────────────────────────┤
     │  AI LAYER  —  LangChain LCEL + Gemini 1.5 Pro      │
     │  5 Agents · Prompt Templates · Guardrails · Memory │
     ├───────────────────────────────────────────────────┤
     │  DATA LAYER  —  ChromaDB + SQLite + File System    │
     │  Vectors · Users · Sessions · Quiz Results         │
     └───────────────────────────────────────────────────┘
                             │
                             ▼
                   Google Gemini 1.5 Pro API
```

| Version | Frontend | Status |
|---|---|---|
| **v1 — IBM SkillsBuild** | Streamlit (`frontend-streamlit/`) | ✅ Complete |
| **v2 — Portfolio** | Next.js 14 + TypeScript + Tailwind (`frontend-web/`) | ✅ Scaffolded |
| **v3 — Roadmap** | Next.js + Clerk + Redis + PostgreSQL | 🔮 Planned |

---

## 🤖 AI Agent System

The `AgentRouter` classifies each user message via `IntentClassifier` (keyword + pattern matching) and dispatches to the correct specialised agent:

| Intent | Agent | What It Does |
|--------|-------|--------------|
| `ask` | **RAGAgent** | Embed question → ChromaDB retrieval → rerank → Gemini → validated answer |
| `quiz` | **QuizAgent** | Retrieve doc chunks → MCQ/T-F/SA prompt → Gemini → JSON parse |
| `summary` | **SummaryAgent** | Broad retrieval → bullet/paragraph prompt → Gemini |
| `flashcard` | **FlashcardAgent** | Key-term retrieval → flashcard prompt → Gemini → JSON parse |
| `teach` | **TeachingAgent** | Context retrieval → explanation prompt → Gemini with analogies |

The **RecommendationEngine** analyses quiz scores per topic, flags weak areas, and calls Gemini to generate a personalised study plan.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.35 | Interactive UI, 5 themes, file upload, dark mode |
| Backend | FastAPI 0.111 + Uvicorn | Async REST API, JWT auth, CORS |
| AI Orchestration | LangChain 0.2 (LCEL) | Agent chains, memory, prompt templates |
| LLM | Google Gemini 1.5 Pro | Text generation, quiz, summary, flashcards |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | 384-dim semantic vectors |
| Vector DB | ChromaDB 0.5 | Cosine similarity search, persistent store |
| Relational DB | SQLite + SQLAlchemy 2 (async) | Users, documents, sessions, quiz results |
| Auth | python-jose (JWT) + bcrypt | Secure token-based authentication |
| File Parsing | PyMuPDF · python-docx · python-pptx | Text extraction from all formats |
| Validation | Pydantic v2 | Request/response schemas, field validators |
| Testing | pytest + pytest-asyncio + httpx | Unit · Integration · Performance |
| CI/CD | GitHub Actions | Lint (Ruff/Black/isort) → Test → Deploy |
| Deployment (BE) | Render | Free-tier Python API hosting |
| Deployment (FE) | Streamlit Cloud | Free Streamlit app hosting |

---

## 📁 Folder Structure

```
study-buddy/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory + lifespan
│   │   ├── config.py               # Pydantic BaseSettings
│   │   ├── database.py             # Async SQLAlchemy engine
│   │   ├── core/                   # security · logging · constants
│   │   ├── middleware/             # Request logger
│   │   ├── dependencies/           # get_db · get_current_user
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic v2 schemas
│   │   ├── repositories/           # Data access layer
│   │   ├── routers/                # API route handlers
│   │   ├── services/               # Business logic
│   │   ├── ai/
│   │   │   ├── agent_router.py     # Central dispatcher
│   │   │   ├── intent_classifier.py
│   │   │   ├── memory_manager.py   # 5 memory types
│   │   │   ├── vector_store.py     # ChromaDB wrapper
│   │   │   ├── gemini_client.py    # LLM + retry
│   │   │   ├── langchain_chains.py
│   │   │   └── agents/             # 5 specialised agents
│   │   ├── prompts/                # Versioned prompt templates
│   │   ├── guardrails/             # Input/output safety
│   │   └── utils/                  # extractor · splitter · validator
│   └── tests/
│       ├── unit/                   # 50+ unit tests
│       ├── integration/            # API integration tests
│       └── performance/            # Latency benchmarks
│
├── frontend/
│   ├── app.py                      # Streamlit entry point
│   ├── pages/                      # 8 pages (landing→help)
│   ├── components/                 # sidebar · auth · uploader · toasts
│   ├── themes/                     # design_system.py (5 themes)
│   └── utils/                      # api_client · session_state
│
├── .github/workflows/              # CI + Deploy GitHub Actions
├── render.yaml                     # Render one-click deploy
├── Dockerfile.backend              # Production Docker image
├── docker-compose.yml              # Local full-stack dev
├── requirements.txt
├── .env.example
└── pyproject.toml                  # Ruff · Black · isort · pytest config
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Google Gemini API Key](https://aistudio.google.com/app/apikey) (free tier available)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/study-buddy.git
cd study-buddy
```

### 2. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env — fill in GOOGLE_API_KEY and SECRET_KEY
```

### 5. Start the backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Start the frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

Open **http://localhost:8501** → Register → Upload a document → Start learning! 🎓

### Docker (optional)
```bash
docker-compose up --build
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | ❌ | Create student account |
| `POST` | `/auth/login` | ❌ | OAuth2 login → JWT token |
| `GET` | `/auth/me` | ✅ | Get current user profile |
| `POST` | `/documents/upload` | ✅ | Upload + index a file |
| `GET` | `/documents/` | ✅ | List user's documents |
| `DELETE` | `/documents/{id}` | ✅ | Delete document + vectors |
| `POST` | `/chat/` | ✅ | Intent-routed AI Q&A |
| `GET` | `/chat/history` | ✅ | Conversation history |
| `DELETE` | `/chat/history` | ✅ | Clear session memory |
| `POST` | `/quiz/generate` | ✅ | Generate quiz questions |
| `POST` | `/quiz/submit` | ✅ | Save quiz result + update scores |
| `POST` | `/summary/` | ✅ | Generate document summary |
| `POST` | `/flashcards/generate` | ✅ | Generate flashcards |
| `GET` | `/dashboard/stats` | ✅ | Aggregated study statistics |
| `GET` | `/health` | ❌ | Liveness probe |

Interactive API docs: **http://localhost:8000/docs**

---

## 🧪 Testing

```bash
# Run all tests with coverage
pytest backend/tests/ --cov=backend/app --cov-report=term-missing -v

# Run only unit tests
pytest backend/tests/unit/ -v

# Run integration tests
pytest backend/tests/integration/ -v

# Run performance benchmarks
pytest backend/tests/performance/ -v
```

**Test coverage targets:** Unit tests >80% · Integration tests cover all 15 endpoints · Performance tests assert latency budgets.

---

## 🚢 Deployment

### Backend → Render

1. Fork this repository on GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repository
4. Render auto-detects `render.yaml` — click **Deploy**
5. In Render Dashboard → Environment → add:
   - `SECRET_KEY` = `$(python -c "import secrets; print(secrets.token_hex(32))")`
   - `GOOGLE_API_KEY` = your Gemini API key

### Frontend → Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub → select repo → set **Main file path** to `frontend/app.py`
3. In **Secrets** (`.streamlit/secrets.toml` format), add:
   ```toml
   API_BASE_URL = "https://your-app.onrender.com"
   ```
4. Click **Deploy**

---

## 📊 Evaluation Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Accuracy | >90% | Manual review of 50 Q&A pairs vs source documents |
| Retrieval Precision | >85% | Top-3 chunks contain answer for 50 test questions |
| API Latency (P95) | <3 sec | httpx timing in integration tests |
| Quiz Quality | >4.0/5.0 | User rating widget after each quiz |
| Hallucination Rate | <5% | Answers contradicting source text / total |
| User Satisfaction | >4.5/5.0 | 5-star feedback widget |
| File Ingestion Success | >98% | SQLite processing status logs |
| Uptime | >99% | UptimeRobot monitoring |

---

## 🗺️ Roadmap

| Version | Milestone | Key Features |
|---------|-----------|--------------|
| **v1.0** ✅ | Core RAG System | Upload, Q&A, ChromaDB, JWT auth, SQLite |
| **v1.5** | Learning Tools | Quiz, flashcards, summaries, conversation memory |
| **v2.0** | AI Agents | Intent routing, 5 specialised agents, recommendation engine |
| **v2.5** | Collaboration | Shared document collections, study groups, PDF export |
| **v3.0** | Voice Assistant | Whisper speech-to-text, audio Q&A |
| **v3.5** | Multilingual | Hindi, Spanish, French — multilingual embeddings |
| **v4.0** | Multimodal AI | Image understanding, video lectures, handwritten OCR |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install pre-commit hooks: `pre-commit install`
4. Make changes and run tests: `pytest backend/tests/`
5. Commit with a descriptive message
6. Open a Pull Request — CI will run automatically

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

## 🙏 Acknowledgements

- **IBM SkillsBuild** — for the internship programme and project guidance
- **Google Gemini API** — for powering the AI generation layer
- **LangChain** — for the RAG orchestration framework
- **ChromaDB** — for the vector store
- **Sentence Transformers** — for the `all-MiniLM-L6-v2` embedding model
- **FastAPI** — for the high-performance async API framework
- **Streamlit** — for making beautiful data apps easy

---

<div align="center">
  <sub>Built with ❤️ as an IBM SkillsBuild Final Project 2025</sub>
</div>
