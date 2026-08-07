# 🎓 AI-Powered Study Buddy

> **IBM SkillsBuild Final Project 2026**  
> An AI-powered learning assistant that helps students upload documents, chat with an AI tutor, generate quizzes, flashcards, and summaries — powered by Google Gemini, RAG, and ChromaDB.

---

## 🏗️ Architecture

```
                    FastAPI Backend
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
  frontend-streamlit             frontend-web
  (IBM Submission ✅)           (Portfolio 🚀 - Coming Soon)
          │                               │
          └───────────────┬───────────────┘
                          ▼
                   Gemini + RAG
                          │
              ┌───────────┴───────────┐
              │                       │
           ChromaDB                SQLite
```

---

## 📂 Project Structure

```
study-buddy/
│
├── backend/                  # FastAPI REST API
│   ├── app/
│   │   ├── routers/          # Auth, Chat, Quiz, Docs, Summary, Flashcards
│   │   ├── services/         # Business logic
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── ai/               # Gemini + RAG pipeline
│   │   ├── core/             # Security, logging, constants
│   │   └── config.py         # Settings (env-driven)
│   └── requirements.txt
│
├── frontend-streamlit/       # IBM SkillsBuild submission
│   ├── app.py                # Main entry point
│   ├── pages/                # Dashboard, Chat, Quiz, etc.
│   ├── components/           # Reusable UI components
│   ├── utils/                # API client, session state
│   └── .streamlit/           # Streamlit config & theme
│
├── frontend-web/             # 🚀 Portfolio Version (Next.js) — Coming Soon
│   ├── app/                  # Next.js App Router
│   ├── components/           # React components
│   ├── services/             # API service layer
│   ├── hooks/                # Custom React hooks
│   ├── types/                # TypeScript types
│   └── styles/               # CSS / Tailwind
│
├── docs/                     # Documentation
│   ├── report/               # Project report
│   ├── presentation/         # Slides / PPT
│   ├── uml/                  # Architecture diagrams
│   └── images/               # Screenshots
│
├── assets/                   # Project assets
│   ├── screenshots/          # App screenshots
│   ├── logos/                # Branding
│   └── demo/                 # Demo videos / GIFs
│
├── shared/                   # Shared utilities (future)
├── docker-compose.yml        # Run everything with one command
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API Key

### 1. Clone the repo
```bash
git clone https://github.com/your-username/AI-Study-Buddy.git
cd AI-Study-Buddy/study-buddy
```

### 2. Set up environment variables
```bash
cp .env.example backend/.env
# Edit backend/.env and add your GOOGLE_API_KEY
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
> API docs available at: http://localhost:8000/docs

### 5. Start the Frontend (Streamlit)
```bash
cd frontend-streamlit
python -m streamlit run app.py
```
> App available at: http://localhost:8501

---

## 🐳 Docker (Run Everything at Once)

```bash
docker-compose up --build
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Document Upload** | Upload PDF, DOCX, PPTX, TXT |
| 💬 **AI Chat** | Chat with your documents using RAG + Gemini |
| 📝 **Quiz Generator** | Auto-generate MCQ quizzes from your notes |
| 🃏 **Flashcards** | Generate flashcards for quick revision |
| 📋 **Summaries** | AI-powered document summarization |
| 📊 **Dashboard** | Track your study progress and scores |
| 🔐 **Authentication** | Secure login with JWT tokens |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — REST API framework
- **Google Gemini** — LLM for AI features
- **ChromaDB** — Vector store for RAG
- **SQLite + SQLAlchemy** — Relational database
- **PyJWT** — Authentication

### Frontend (IBM Version)
- **Streamlit** — Python-native web UI

### Frontend (Portfolio Version — Planned)
- **Next.js 14** — React framework
- **Tailwind CSS** — Styling
- **TypeScript** — Type safety

---

## 📌 Versions

| Version | Frontend | Status |
|---|---|---|
| **v1.0 — IBM Edition** | Streamlit | ✅ Active |
| **v2.0 — Portfolio Edition** | Next.js | 🚀 Planned |

---

## 👩‍💻 Author

**Piyu** — IBM SkillsBuild Internship 2026  
*Data Science & AI Engineering Track*

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
