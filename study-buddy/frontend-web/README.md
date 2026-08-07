# 🚀 AI Study Buddy — Modern Web Frontend (Portfolio Edition)

> **Status:** 🔧 Coming Soon — Planned after IBM SkillsBuild submission.

This folder will contain the **Next.js / React** version of the AI-Powered Study Buddy frontend.

It connects to the **exact same FastAPI backend** as the Streamlit version — no backend changes required.

---

## Planned Tech Stack

| Technology | Purpose |
|---|---|
| **Next.js 14** (App Router) | React framework |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Animations |
| **ShadCN UI** | Component library |
| **Clerk** (optional) | Authentication |
| **React Query** | Server state management |

---

## Planned Folder Structure

```
frontend-web/
│
├── app/                  # Next.js App Router pages
│   ├── (auth)/           # Login / Register layouts
│   ├── dashboard/
│   ├── chat/
│   ├── quiz/
│   ├── flashcards/
│   ├── summary/
│   ├── profile/
│   └── settings/
│
├── components/           # Reusable React components
│   ├── ui/               # Base UI components
│   ├── layout/           # Navbar, Sidebar, Footer
│   └── features/         # Feature-specific components
│
├── services/             # API service layer (calls FastAPI)
├── hooks/                # Custom React hooks
├── types/                # TypeScript type definitions
├── lib/                  # Utility functions
├── styles/               # Global CSS
└── public/               # Static assets
```

---

## API Endpoints (Same as Streamlit version)

```
POST   /auth/register
POST   /auth/login
GET    /auth/me

POST   /documents/upload
GET    /documents/

POST   /chat/
DELETE /chat/history

POST   /quiz/generate
POST   /quiz/submit

POST   /summary/generate

POST   /flashcards/generate

GET    /dashboard/stats
```

---

## How to Start (Once Built)

```bash
cd frontend-web
npm install
npm run dev
```

App will run on http://localhost:3000

---

> 💡 The FastAPI backend runs on port **8000** and serves both this frontend and the Streamlit version seamlessly.
