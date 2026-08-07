# AI-Powered Study Buddy — Next.js Web Frontend
# Version 2.0 (Portfolio Edition)

## Status

> ✅ **Scaffolded and ready.** Connect to the existing FastAPI backend.

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 14 (App Router) | React framework with SSR/SSG |
| **TypeScript** | 5.5 | Type safety across all components |
| **Tailwind CSS** | 3.4 | Utility-first styling |
| **TanStack Query** | 5 | Server state management + caching |
| **Zustand** | 4.5 | Client-side auth state |
| **Framer Motion** | 11 | Page transitions and animations |
| **next-themes** | 0.3 | Dark/Light/System theme switching |
| **react-dropzone** | 14 | Drag-and-drop file upload |
| **react-hot-toast** | 2.4 | Toast notification system |
| **axios** | 1.7 | HTTP client (typed, interceptors) |

## Architecture

```
frontend-web/
│
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout + ThemeProvider + QueryClient
│   ├── providers.tsx             # All client-side providers
│   ├── page.tsx                  # Landing page (Server Component)
│   ├── (auth)/                   # Auth route group
│   │   ├── layout.tsx            # Centred auth card layout
│   │   ├── login/page.tsx        # Sign-in form
│   │   └── register/page.tsx     # Registration form
│   └── (app)/                    # Protected route group
│       ├── layout.tsx            # Sidebar + auth guard
│       ├── dashboard/page.tsx    # KPIs, topic progress, AI tips
│       ├── chat/page.tsx         # Multi-turn RAG chat
│       ├── quiz/page.tsx         # Quiz generation + auto-score
│       ├── flashcards/page.tsx   # Flip card study interface
│       ├── summary/page.tsx      # AI document summarisation
│       ├── profile/page.tsx      # User profile + document manager
│       └── settings/page.tsx     # Theme + AI preferences
│
├── components/                   # Shared React components (to grow)
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts                # Login, register, logout, current user
│   ├── useDocuments.ts           # Upload, list, delete documents
│   └── useChat.ts                # RAG chat with optimistic updates
│
├── services/
│   └── api.ts                    # Typed axios calls to all FastAPI endpoints
│
├── lib/
│   ├── utils.ts                  # cn(), formatDate, scoreColor, uuid...
│   └── auth.ts                   # JWT decode, saveSession, clearSession
│
├── types/
│   └── index.ts                  # All TypeScript types (mirrors Pydantic schemas)
│
├── styles/
│   └── globals.css               # Tailwind base + CSS variables + prose styles
│
├── public/                       # Static assets
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config with path aliases
├── tailwind.config.ts            # Tailwind config with custom tokens
├── next.config.ts                # Next.js config with /api proxy rewrite
└── .env.local.example            # Environment variables template
```

## Quick Start

```bash
# Install dependencies
cd frontend-web
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL if not using default

# Make sure backend is running first:
# cd ../backend && uvicorn app.main:app --reload

# Start Next.js dev server
npm run dev

# App runs at: http://localhost:3000
# API docs at: http://localhost:8000/docs
```

## Design System

The design system mirrors the Streamlit version's token set:

| Token | Light | Dark |
|---|---|---|
| Background | `#f8fafc` | `#0f1117` |
| Surface | `#ffffff` | `#1e2130` |
| Border | `#e2e8f0` | `#2d3748` |
| Accent | `#2563eb` | `#3b82f6` |
| Text | `#1e293b` | `#e2e8f0` |
| Muted | `#64748b` | `#94a3b8` |

## Roadmap

| Version | Feature | Status |
|---|---|---|
| v2.0 | Full Next.js App Router scaffold | ✅ Done |
| v2.1 | Framer Motion page transitions | Planned |
| v2.2 | PWA manifest + offline support | Planned |
| v3.0 | Clerk authentication + social login | Planned |
| v3.0 | PostgreSQL + Redis (Render managed) | Planned |
| v3.1 | Real-time collaboration rooms (WebSocket) | Planned |

## API Endpoints

This frontend connects to the same FastAPI backend as the Streamlit version.
See `docs/api/` for full endpoint documentation.

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

POST   /api/v1/documents/upload
GET    /api/v1/documents/
DELETE /api/v1/documents/{id}

POST   /api/v1/chat/
GET    /api/v1/chat/history
DELETE /api/v1/chat/history

POST   /api/v1/quiz/generate
POST   /api/v1/quiz/submit

POST   /api/v1/summary/

POST   /api/v1/flashcards/generate

GET    /api/v1/dashboard/
```

---

> 💡 One backend. Two frontends. The FastAPI backend serves both the Streamlit IBM version and this Next.js portfolio version without any changes.
