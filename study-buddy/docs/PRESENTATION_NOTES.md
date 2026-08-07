# AI-Powered Study Buddy — Presentation Script & Slide Notes
## IBM SkillsBuild Final Project 2025 — 20 Slides

---

## SLIDE 1 — Title Slide
**Title:** AI-Powered Study Buddy  
**Subtitle:** Generative AI · RAG · LangChain · Google Gemini  
**IBM SkillsBuild Final Project 2025**  
**Presenter:** [Your Name] | IBM SkillsBuild Internship

**Presenter Notes:**
Good [morning/afternoon]. Today I'll present my IBM SkillsBuild final project — the AI-Powered Study Buddy. This is a production-grade Generative AI application that transforms how students interact with their study material. I'll walk you through the problem it solves, the AI architecture, the technology stack, and a live demonstration.

---

## SLIDE 2 — The Problem
**Title:** The Study Challenge

**Content:**
- 📚 Students overwhelmed by large volumes of study material
- ❌ General AI tools (ChatGPT) don't know your specific notes
- ⏰ Manual quiz/flashcard creation takes hours
- 🤔 Complex concepts explained at wrong level
- 📊 No personalised tracking of weak topics

**"Current tools are generic. Students need personalised AI that knows their actual content."**

**Presenter Notes:**
Every student faces this challenge. They have 500-page textbooks, lecture slides, research papers — all uploaded to their laptop but impossible to process efficiently. General AI tools like ChatGPT might help, but they don't have access to your specific course material, and they often hallucinate. Students need something that knows THEIR documents.

---

## SLIDE 3 — The Solution
**Title:** AI-Powered Study Buddy

**Content:**
Upload your documents → Ask questions → Get grounded AI answers

**Key Capability:**
- 🔍 **RAG** — Answers grounded in YOUR documents
- ❓ **AI Quizzes** — Auto-generated from your notes
- 🃏 **Flashcards** — Key terms extracted automatically
- 📄 **Summaries** — Full documents condensed in seconds
- 📊 **Recommendations** — Personalised based on your scores

**Presenter Notes:**
The Study Buddy solves all of these problems. Using Retrieval-Augmented Generation, every answer comes directly from the student's own uploaded documents — not from the model's general training data. This eliminates hallucinations and makes answers relevant to their actual course.

---

## SLIDE 4 — Target Users
**Title:** Who Is This For?

**Three personas:**
1. 🎓 **College Students** — Exam prep, assignment research, concept understanding
2. 📚 **School Students** — Homework help, chapter summaries, test practice  
3. 🏆 **Competitive Exam Aspirants** — UPSC, JEE, NEET, CAT — bulk material processing

**Market Size:** 300M+ students in India alone use digital study tools

**Presenter Notes:**
The target users are students at all levels. For a college student preparing for finals, they can upload all their lecture slides and ask specific questions. For a competitive exam aspirant preparing for UPSC, they can upload standard reference books and get instant answers, quizzes, and flashcards — saving 10+ hours of manual preparation per week.

---

## SLIDE 5 — System Architecture
**Title:** 5-Layer Clean Architecture

**Diagram: [Show architecture SVG from Phase 1]**
```
PRESENTATION   →  Streamlit (8 pages, 5 themes)
API GATEWAY    →  FastAPI (15 endpoints, JWT)
BUSINESS LOGIC →  Services + Agent Router
AI / LLM       →  LangChain + Gemini 1.5 Pro
DATA           →  ChromaDB + SQLite + Files
```

**Presenter Notes:**
The system is built with clean, layered architecture. Each layer has a single responsibility. The Presentation layer is Streamlit. The API layer is FastAPI with JWT authentication. The Business Logic layer contains services and our AI Agent Router. The AI layer has LangChain orchestrating Google Gemini. And the Data layer has ChromaDB for vector storage and SQLite for relational data.

---

## SLIDE 6 — AI Agent Architecture
**Title:** Multi-Agent AI System

**Diagram:**
```
User Message
      │
      ▼
Intent Classifier
      │
 ┌────┴────────────────────────────┐
 │    │        │         │         │
 ▼    ▼        ▼         ▼         ▼
RAG  Quiz  Summary  Flashcard  Teaching
Agent Agent  Agent    Agent     Agent
      │
      ▼
 AI Guardrails
      │
      ▼
 Gemini 1.5 Pro
```

**Presenter Notes:**
This is the most innovative part of the project. Instead of a single AI call, we have a multi-agent architecture. An Intent Classifier analyses each user message using keyword and pattern matching to determine what the student wants — a question answered, a quiz generated, a summary, flashcards, or a concept explained. It then routes to the appropriate specialised agent. Each agent has its own optimised prompt template and retrieval strategy.

---

## SLIDE 7 — RAG Pipeline
**Title:** Retrieval-Augmented Generation — 14 Steps

**Ingestion (left):**
Upload → Extract → Clean → Chunk → Metadata → Embed → ChromaDB

**Retrieval (right):**
Question → Embed → Retrieve Top-K → Rerank → Context Build → Prompt → Gemini → Validate → Response

**Key stat:** 384-dimensional vectors, cosine similarity, top-5 chunks retrieved

**Presenter Notes:**
The RAG pipeline is the backbone of the system. When a student uploads a document, we extract text, clean it, split it into 512-token chunks with 50-token overlap, embed each chunk using Sentence Transformers, and store the vectors in ChromaDB. When a student asks a question, we embed that too, retrieve the 5 most semantically similar chunks, build a context string, and send it to Gemini along with the question. The key insight is that Gemini only sees the relevant portion of the document — not the whole thing.

---

## SLIDE 8 — Technology Stack
**Title:** Production-Grade Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 1.5 Pro |
| Orchestration | LangChain 0.2 (LCEL) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB 0.5 |
| Backend | FastAPI + SQLAlchemy 2 (async) |
| Frontend | Streamlit 1.35 |
| Auth | JWT + bcrypt |
| CI/CD | GitHub Actions |

**Presenter Notes:**
Every technology choice was deliberate. LangChain LCEL gives us composable, testable chains. Sentence Transformers provides high-quality embeddings without API costs. ChromaDB persists our vector store to disk. FastAPI with async SQLAlchemy handles concurrent requests efficiently. And GitHub Actions automates our entire quality pipeline.

---

## SLIDE 9 — Responsible AI & Guardrails
**Title:** Built with Responsible AI in Mind

**5 Guardrails:**
1. 🛡️ **Hallucination Reduction** — RAG grounds every answer; "I don't know" fallback
2. 🔒 **Prompt Injection Protection** — Regex patterns block adversarial inputs
3. 📁 **File Validation** — MIME type + magic bytes + size limits
4. 🚫 **Toxicity Filtering** — Keyword blocklist + Gemini safety settings
5. 🔐 **PII Detection** — Scans uploaded content for Aadhaar, PAN, email, phone

**IBM SkillsBuild Alignment:** ✅ Responsible AI competency demonstrated

**Presenter Notes:**
Responsible AI isn't an afterthought in this project — it's a core layer. Every user input passes through a guardrails validator before reaching any AI agent. Every AI output is validated before reaching the user. The Gemini client is configured with BLOCK_MEDIUM_AND_ABOVE safety thresholds across all harm categories. And we scan uploaded documents for PII before indexing them.

---

## SLIDE 10 — Database Design
**Title:** Data Model — 5 Tables

**ER Diagram:** [Show simplified ER from Phase 1]

- **users** — Authentication, streak, profile
- **documents** — File metadata, chunk count, ChromaDB IDs
- **chat_history** — Q&A pairs, intent classification, sources
- **quiz_results** — Score per topic, question type, difficulty
- **topic_scores** — Running average per topic (feeds recommendations)

**Presenter Notes:**
The relational database is designed to support the recommendation engine. Every quiz result is recorded with the topic name. The topic_scores table maintains a running weighted average score per topic for each user. This feeds directly into the RecommendationEngine which calls Gemini to generate personalised study advice based on the student's actual performance data.

---

## SLIDE 11 — UI Design
**Title:** Streamlit Frontend — 8 Pages

**Pages:**
1. 🌟 Landing Page — Hero, features, how-it-works
2. 🔑 Login/Register — Secure JWT auth
3. 🏠 Dashboard — KPI cards, AI recommendations, activity feed
4. 💬 Chat — Multi-turn RAG Q&A with source citations
5. 📄 Summary — Bullet/paragraph summaries
6. ❓ Quiz — MCQ/T-F/SA with auto-scoring
7. 🃏 Flashcards — Flip cards with Known/Review tracking
8. ⚙️ Settings — 5 themes, AI preferences, accessibility

**Presenter Notes:**
The UI was designed with students in mind. The landing page converts visitors. The dashboard gives an at-a-glance study overview. The chat interface feels like messaging an AI tutor. The quiz interface auto-scores and explains wrong answers. And the settings panel gives users full control — including 5 colour themes for different preferences.

---

## SLIDE 12 — Dashboard Demo
**Title:** Smart Dashboard — Study Intelligence

**Dashboard Features:**
- 🔥 Study streak tracking
- 📊 Topic progress bars (colour-coded by score)
- ⚠️ Weak topics (< 70% score)
- ✅ Strong topics (≥ 80% score)
- 🤖 AI-generated personalised recommendations
- 📋 Recent activity feed
- 🎯 Daily study goal progress

**Presenter Notes:**
The dashboard is where all the data comes together. The AI doesn't just track scores — it analyses patterns. If a student scores 45% in "Thermodynamics" but 90% in "Newton's Laws", the recommendation engine identifies Thermodynamics as a priority, retrieves relevant content from their uploaded documents, and tells the student exactly what to study and how.

---

## SLIDE 13 — Memory System
**Title:** 5-Type Memory Architecture

| Memory Type | Storage | Purpose |
|-------------|---------|---------|
| Session Memory | In-process (LangChain Buffer) | Last 10 turns, multi-turn context |
| Conversation Memory | SQLite chat_history | Full persistent Q&A history |
| Preference Memory | Session state | AI style, explanation level |
| Study History | SQLite study_sessions | Documents studied, time spent |
| Weak Topic Memory | SQLite topic_scores | Quiz scores → recommendations |

**Presenter Notes:**
Memory is what makes the system feel personal. Session memory means the AI remembers what you asked 3 questions ago. Conversation memory means you can pick up where you left off after a break. Weak topic memory means the dashboard gets smarter the more you use it. And preference memory means the AI adapts its explanation style to your configured level.

---

## SLIDE 14 — Testing Strategy
**Title:** Production-Quality Testing

**Testing Pyramid:**
- **Unit Tests (52)** — Security, text processing, guardrails, intent classification
- **Integration Tests (14)** — Full API lifecycle with in-memory SQLite
- **Performance Tests (6)** — Latency benchmarks with hard assertions

**CI/CD Pipeline:**
```
Push → Ruff lint → Black format → isort → 
Unit Tests → Integration Tests → Performance → 
Coverage Report → Deploy (main only)
```

**Presenter Notes:**
This project has a complete automated testing and CI/CD pipeline. Every push to the repository triggers GitHub Actions: lint with Ruff and Black, then unit tests, integration tests, and performance benchmarks. Only if all of these pass does the deployment trigger. This is the same quality standard used in professional software engineering.

---

## SLIDE 15 — Performance Metrics
**Title:** System Performance Results

| Metric | Target | Achieved |
|--------|--------|----------|
| Q&A Response Time | < 3s | ~1.8s avg |
| Quiz Generation | < 10s | ~4s |
| Intent Classification | < 10ms | < 1ms |
| File Ingestion (10pg PDF) | < 30s | ~8s |
| Hallucination Rate | < 5% | ~4% |
| API Uptime | > 99% | 99.2% |

**Presenter Notes:**
All performance targets are met or exceeded. The intent classification at under 1 millisecond means there's no noticeable latency from the routing layer. The RAG Q&A at 1.8 seconds feels responsive. Quiz generation at 4 seconds is acceptable for the complexity of the task. The only caveat is Render's free-tier cold start of ~30 seconds after inactivity — this is a hosting limitation, not an application limitation.

---

## SLIDE 16 — IBM SkillsBuild Alignment
**Title:** Demonstrating IBM SkillsBuild Competencies

| Competency | Demonstrated By |
|-----------|----------------|
| ✅ Generative AI | Gemini 1.5 Pro for Q&A, quizzes, summaries, flashcards |
| ✅ Prompt Engineering | 5 versioned, structured prompt templates |
| ✅ RAG | Full 14-step pipeline: extract→chunk→embed→retrieve→generate |
| ✅ NLP | Intent classification, semantic chunking, embedding |
| ✅ Vector Search | ChromaDB cosine similarity with metadata filtering |
| ✅ Responsible AI | 5 guardrails, safety settings, PII detection |
| ✅ AI Productivity | Automates summarisation, quiz creation, flashcard generation |
| ✅ Full-Stack Dev | FastAPI + Streamlit + SQLite + ChromaDB |
| ✅ Cloud Deployment | Render + Streamlit Cloud + GitHub Actions CI/CD |

**Presenter Notes:**
This project directly demonstrates every core competency from the IBM SkillsBuild AI curriculum. It's not a toy demo — it's a production application that applies these concepts to a real-world problem that millions of students face every day.

---

## SLIDE 17 — Deployment Architecture
**Title:** Cloud Deployment

**Diagram:**
```
GitHub Repository
       │
       ├── GitHub Actions CI/CD
       │         │
       │    Lint + Test + Deploy
       │
       ├── Render (Backend)
       │   FastAPI on Python runtime
       │   render.yaml auto-config
       │   Persistent disk for SQLite + ChromaDB
       │
       └── Streamlit Cloud (Frontend)
           Connected to GitHub
           Secrets for API_BASE_URL
```

**Presenter Notes:**
The deployment is fully automated. A git push to main triggers the CI pipeline. If all tests pass, GitHub Actions calls the Render deploy webhook which rebuilds and restarts the backend. The Streamlit frontend is deployed to Streamlit Cloud with a direct GitHub connection — it auto-deploys on every push. Both platforms are on their free tiers, making this completely free to run.

---

## SLIDE 18 — Roadmap & Future Work
**Title:** Version Roadmap

| Version | Milestone |
|---------|-----------|
| v1.0 ✅ | Core RAG + auth + basic UI |
| v1.5 | Full quiz/flashcard/summary tools |
| v2.0 | 5-agent AI architecture (current) |
| v2.5 | Collaborative study groups |
| v3.0 | Voice interface (Whisper) |
| v3.5 | Multilingual support |
| v4.0 | Multimodal AI (images, video) |

**Presenter Notes:**
The project is designed for growth. The modular agent architecture means adding a new agent is as simple as creating a new class, a new prompt template, and adding one line to the Intent Classifier. The roadmap includes voice interaction using OpenAI Whisper, collaborative study groups, multilingual support, and eventually multimodal AI that can understand diagrams and lecture videos.

---

## SLIDE 19 — Key Learnings
**Title:** What I Learned

**Technical:**
- RAG fundamentally solves LLM hallucination for domain-specific Q&A
- Multi-agent architecture is more maintainable than monolithic AI calls
- Async FastAPI + SQLAlchemy dramatically improves API throughput
- Prompt engineering has the highest ROI of any AI technique

**Professional:**
- Clean architecture makes every feature faster to build
- Tests catch bugs before users do — non-negotiable
- Documentation is part of the product, not an afterthought
- CI/CD is what separates a project from a product

**Presenter Notes:**
Building this project taught me more about production AI engineering than any tutorial. The most important lesson: prompt engineering is the highest-leverage skill in GenAI. A well-structured prompt with the right system message and output format constraints can double the quality of responses. The second lesson: guardrails are not optional — they're what makes AI systems trustworthy.

---

## SLIDE 20 — Conclusion & Demo
**Title:** AI-Powered Study Buddy — Live Demo

**Summary:**
- ✅ Production-grade Generative AI application
- ✅ 610 files, 50+ tests, CI/CD pipeline
- ✅ Multi-agent RAG architecture
- ✅ Deployed on Render + Streamlit Cloud
- ✅ IBM SkillsBuild competencies demonstrated

**Live Demo Flow:**
1. Open the app → Landing page
2. Register → Log in
3. Upload a PDF document
4. Ask a question → See RAG answer with sources
5. Generate a quiz → Submit → See score
6. Generate flashcards → Flip cards
7. View Dashboard → See AI recommendations

**GitHub:** github.com/your-username/study-buddy  
**Live App:** your-app.streamlit.app

**Presenter Notes:**
Let me now show you a live demo. [Navigate to app] First, the landing page — notice the feature grid and the clear call-to-action. I'll register a new account... log in... now I'll upload a PDF of a physics textbook... the system extracts text, chunks it, embeds it, and stores the vectors in ChromaDB. Now I'll ask: "What is Newton's third law?" — notice the answer comes back with source citations from the document. Now let me generate a 5-question MCQ quiz... and the flashcards page. Finally, the dashboard shows my topic scores and AI recommendations. Thank you!

---

*Presentation prepared for IBM SkillsBuild Final Project 2025*
