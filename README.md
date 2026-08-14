<div align="center">

# ✂️ AI Fashion Design Generator

### Transform Fashion Ideas into AI-Generated Designs, Recommendations & Virtual Try-On

<p><strong>IBM Internship 2026 Project &nbsp;·&nbsp; v2.0.0</strong></p>

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Cloudflare Workers AI](https://img.shields.io/badge/Cloudflare-Workers_AI-F38020?style=flat-square&logo=cloudflare&logoColor=white)](https://developers.cloudflare.com/workers-ai/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![Hugging Face](https://img.shields.io/badge/Hugging_Face-IDM--VTON-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/yisol/IDM-VTON)
[![RapidAPI](https://img.shields.io/badge/RapidAPI-H%26M_Store-0055DA?style=flat-square&logo=rapidapi&logoColor=white)](https://rapidapi.com)
[![IBM Internship](https://img.shields.io/badge/IBM-Internship_2026-054ADA?style=flat-square&logo=ibm&logoColor=white)](https://ibm.com)

<p>
  <a href="#-quick-start">Quick Start</a> &nbsp;·&nbsp;
  <a href="#-api-reference">API Reference</a> &nbsp;·&nbsp;
  <a href="#-how-it-works">Architecture</a> &nbsp;·&nbsp;
  <a href="#-security">Security</a> &nbsp;·&nbsp;
  <a href="README-API-SETUP.md">Full API Setup Guide</a> &nbsp;·&nbsp;
  <a href="#-license">License</a>
</p>

</div>

---

> Describe an outfit in natural language. Generate the design, discover matching products, and visualize the garment with AI-powered virtual try-on — all in one unified workflow.

---

<p align="center">
  <img src="public/screenshots/DASHBOARD.jpeg" alt="AI Fashion Studio Dashboard" width="100%">
</p>

<p align="center"><strong>AI Fashion Studio — unified fashion ideation and visualization workflow</strong></p>

---

## Why This Project?

### The Problem

Fashion ideation today is fragmented and inaccessible:

- Requires design expertise or expensive tools (Figma, Adobe, CLO 3D)
- Prompt-to-image tools give generic results — no fashion intelligence layer
- Product discovery and virtual try-on live in entirely separate applications
- No single workflow takes you from a text idea to a wearable design concept

### The Solution

**AI Fashion Design Generator** consolidates the entire workflow into one application:

```
Natural Language Prompt
         ↓
  Gemini Fashion Spec Extraction
  (category · fabric · color · style · budget)
         ↓
  Prompt Optimization
         ↓
  Cloudflare Workers AI → Fashion Design Image
         ↓
  RapidAPI H&M Product Search + Ranking
         ↓
  IDM-VTON Virtual Try-On
         ↓
  Saved Collection / Tech Pack Export
```

---

## Core Features

| Feature | Description |
|---|---|
| **AI Design Studio** | Text-to-fashion image generation with 4 selectable Cloudflare Workers AI models |
| **Fashion Intelligence** | Gemini extracts category, fabric, colors, sustainability score, budget, and style from plain text |
| **Model Selector** | Switch between FLUX.1 Schnell, SDXL, DreamShaper, SDXL Lightning |
| **Product Recommendations** | Real H&M products fetched via RapidAPI, ranked by category · color · budget · style |
| **Virtual Try-On** | AI-powered garment transfer prototype using IDM-VTON via Hugging Face |
| **Tech Pack** | Export a manufacturing-oriented specification sheet |
| **Collections** | Save generated designs locally for later review |
| **Secure API Architecture** | All credentials (Cloudflare, HF, RapidAPI) are strictly server-side — never exposed to the browser |
| **Eco Score** | Sustainability scoring per design |

---

## Deployment Architecture

This project uses **two complementary API layers** — one for each deployment context:

| Context | API Layer | Entry Point |
|---|---|---|
| **Vercel (production)** | Python serverless functions | `api/*.py` |
| **Local development** | FastAPI server | `backend/app/main.py` |

Both layers implement the same endpoints (`/api/design`, `/api/try-on`, `/api/products/search`, `/api/health`) and consume the same environment variables. The Vercel functions are the primary deployment path. The FastAPI backend is the local development and testing reference implementation.

```
── Vercel (production) ───────────────────────────
  React (dist/)
       ↓
  Vercel Serverless Functions (api/*.py)
       ↓ rewrites via vercel.json
  /api/design         → api/design.py
  /api/try-on         → api/try-on.py
  /api/products/search → api/products.py
  /api/health         → api/health.py

── Local development ─────────────────────────────
  React (Vite dev server :5173)
       ↓
  FastAPI server (:8000)  (backend/app/main.py)
       ↓
  backend/app/api/{design,tryon,products}.py
```

> The dual-layer design is intentional: Vercel serverless functions are stateless and suited for production deployment, while FastAPI provides a richer local development experience with async support, Pydantic validation, structured logging, and `pytest`-based testing.

---

## How It Works

### System Architecture

```
┌─────────────────────────────────┐
│         React Frontend          │
│         Vite 8 + Tailwind 4     │
└───────────────┬─────────────────┘
                │  HTTP (JSON / multipart)
                ▼
┌─────────────────────────────────────────────┐
│  API Layer                                  │
│  Vercel serverless (production)             │
│  — or —                                     │
│  FastAPI + uvicorn (local dev)              │
│  Routing · Validation · CORS · Rate Limits  │
└──────┬───────────┬──────────────┬───────────┘
       │           │              │
       ▼           ▼              ▼
  Cloudflare    RapidAPI      IDM-VTON
  Workers AI    H&M Store     Hugging Face
  (image gen)   (products)    (try-on)

  Google Gemini  ←  client-side only (spec extraction)
```

### Integration Summary

| Integration | Role |
|---|---|
| **Google Gemini 2.5 Flash** | Client-side fashion spec extraction — extracts structured attributes from free-text descriptions |
| **Cloudflare Workers AI** | Server-side image generation — FLUX.1, SDXL, DreamShaper, SDXL Lightning models |
| **RapidAPI H&M Store** | Server-side product search — fetches real H&M catalogue items matched to the design |
| **IDM-VTON (Hugging Face)** | Server-side virtual try-on — third-party AI model; composites person and garment images |

---

## AI Pipeline

```
User Prompt (free text)
        ↓
  Google Gemini 2.5 Flash
  → Fashion Specification JSON
    (category, fabric, colors, style, budget, sustainability)
        ↓
  Prompt Optimization
  (structured prompt for image generation)
        ↓
  FastAPI → Cloudflare Workers AI
  → Generated Fashion Design Image (base64 PNG)
        ↓
  FastAPI → RapidAPI H&M Store
  → Product Candidates → Ranked Results
        ↓
  FastAPI → Hugging Face IDM-VTON
  → Virtual Try-On Composite Image
```

The pipeline separates concerns: Gemini handles language understanding client-side, while all credential-bearing API calls (Cloudflare, RapidAPI, Hugging Face) run exclusively through the server-side API layer.

---

## Supported Image Models

Select any model from the **AI Model** dropdown in the Studio tab:

| Model | Best For |
|---|---|
| `@cf/black-forest-labs/flux-1-schnell` | Best quality / speed ratio for fashion renders |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | Higher detail, slightly slower |
| `@cf/lykon/dreamshaper-8-lcm` | Painterly, creative illustrations |
| `@cf/bytedance/stable-diffusion-xl-lightning` | Ultra-fast 4-step generation |

---

## Product Recommendation Engine

Products are retrieved through the **RapidAPI H&M Store API** and ranked using a weighted scoring algorithm based on available product metadata:

| Signal | Weight |
|---|---|
| Category match | 40 pts |
| Color match | 25 pts |
| Budget fit | 20 pts |
| Style / brand | 15 pts |

No vector similarity or semantic embeddings are used — ranking is based on structured metadata matching.

---

## Virtual Try-On

```
Person Photo (full-body)
        +
Garment Image (clean product photo or uploaded image)
        ↓
  API Layer → Hugging Face Space: yisol/IDM-VTON
  (gradio_client · ZeroGPU · auto-crop · 40 denoise steps)
        ↓
  AI Try-On Result Image
```

**IDM-VTON** is a third-party AI model developed by [yisol](https://github.com/yisol/IDM-VTON). This project integrates it via its public Hugging Face Space using `gradio_client` — IDM-VTON was not trained or developed as part of this project.

**Note on garment images:** IDM-VTON performs best with a clean, isolated garment photograph. When using an AI-generated design image as the garment input, results may vary because the generated image typically includes a full scene (person, background, garment) rather than a cropped garment-only image. The auto-crop option (`is_checked_crop=True`) is enabled to partially mitigate this.

- **License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (non-commercial)
- **Repository:** [https://github.com/yisol/IDM-VTON](https://github.com/yisol/IDM-VTON)
- **Hugging Face Space:** [https://huggingface.co/spaces/yisol/IDM-VTON](https://huggingface.co/spaces/yisol/IDM-VTON)

Use of this integration is subject to IDM-VTON's non-commercial license terms.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite 8, Tailwind CSS 4, lucide-react |
| Backend — Local dev | Python 3.11, FastAPI 0.115, Pydantic v2, httpx, slowapi |
| Backend — Production | Python 3.11 serverless functions, gradio_client, stdlib urllib |
| AI — Image Generation | Cloudflare Workers AI (FLUX.1, SDXL, DreamShaper) |
| AI — Language | Google Gemini 2.5 Flash |
| Virtual Try-On | IDM-VTON via Hugging Face Spaces (gradio_client) |
| Product Data | RapidAPI H&M Store API |
| Deployment | Vercel (React SPA + Python serverless functions) |
| Development | Git, GitHub |

---

## Project Structure

```
AI-Fashion-Design-Generator-IBM-INTERSHIP-2026/
├── src/
│   ├── App.jsx              # Main React component — all UI
│   ├── main.jsx             # React root mount
│   └── index.css            # Tailwind v4 entry
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app · CORS · rate limiting · health
│   │   ├── api/
│   │   │   ├── design.py    # POST /api/design
│   │   │   ├── products.py  # GET  /api/products/search
│   │   │   └── tryon.py     # POST /api/try-on
│   │   ├── services/
│   │   │   ├── cloudflare_ai.py  # Cloudflare Workers AI integration
│   │   │   ├── idm_vton.py       # Hugging Face IDM-VTON integration
│   │   │   └── product_api.py    # RapidAPI H&M integration
│   │   └── schemas/
│   │       ├── design.py         # Pydantic models · model allowlist
│   │       └── product.py        # Product response schema
│   ├── tests/
│   │   ├── test_design.py        # Design endpoint tests (fully mocked)
│   │   └── test_products.py      # Product endpoint tests (fully mocked)
│   └── requirements.txt
│
├── api/                     # Vercel serverless functions (alternative deploy)
│   ├── design.py            # POST /api/design
│   ├── products.py          # GET  /api/products/search
│   ├── try-on.py            # POST /api/try-on
│   └── health.py            # GET  /api/health
│
├── samples/                 # Sample wardrobe images (16 outfits)
│
├── public/
│   └── screenshots/         # README screenshots
│
├── index.html               # Vite entry point
├── vite.config.js           # Vite + Tailwind v4 + React plugin
├── vercel.json              # Vercel deployment configuration
├── .env.example             # Template — copy to .env
├── README.md
└── README-API-SETUP.md      # Detailed API and environment setup guide
```

---

## Screenshots

### Dashboard — Runway & Trending Concepts

<p align="center">
  <img src="public/screenshots/DASHBOARD.jpeg" alt="AI Fashion Studio Dashboard" width="100%">
</p>

### Studio — Generated Design Output

<p align="center">
  <img src="public/screenshots/generated-output.png" alt="Generated Design Output" width="100%">
</p>

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- A free [Cloudflare account](https://dash.cloudflare.com)

### 1. Clone & install

```bash
git clone https://github.com/Piyu242005/AI-Fashion-Design-Generator-IBM-INTERSHIP-2026.git
cd AI-Fashion-Design-Generator-IBM-INTERSHIP-2026
npm install
```

### 2. Configure environment

```bash
cp .env.example .env     # macOS / Linux
copy .env.example .env   # Windows
```

Open `.env` and populate the required variables (see [Environment Variables](#-environment-variables)).

### 3. Start the FastAPI backend (local dev)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify the backend is running:

```
GET http://localhost:8000/api/health
```

### 5. Start the React frontend

```bash
# In a new terminal from the project root
npm run dev
```

Open **http://localhost:5173**

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values below.

> **Never commit `.env`.** It is already excluded by `.gitignore`.

### Frontend-visible (browser-safe)

| Variable | Description |
|---|---|
| `VITE_GEMINI_API_KEY` | Google AI Studio API key — used client-side for fashion spec extraction |
| `VITE_GEMINI_MODEL` | Gemini model to use (default: `gemini-2.5-flash`) |

`VITE_*` variables are intentionally exposed to the browser. Only the Gemini key is placed here because spec extraction runs client-side. Never put Cloudflare, Hugging Face, or RapidAPI keys under a `VITE_` prefix.

### Backend secrets (server-side only)

| Variable | Description |
|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID — required for image generation |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Workers AI API token — required for image generation |
| `HF_TOKEN` | Hugging Face token (READ permission) — for authenticated IDM-VTON access |
| `HF_SPACE_ID` | Hugging Face Space ID (default: `yisol/IDM-VTON`) |
| `RAPIDAPI_KEY` | RapidAPI key — required for product recommendations |
| `RAPIDAPI_HOST` | RapidAPI host (default: `apidojo-hm-hennes-mauritz-v1.p.rapidapi.com`) |

Full setup instructions for each provider: [README-API-SETUP.md](README-API-SETUP.md)

---

## API Reference

Base URL (local dev): `http://localhost:8000`

---

### `POST /api/design`

Generate a fashion image via Cloudflare Workers AI.

**Request body** (`application/json`)

```json
{
  "prompt": "Modern Indian half-saree in pastel pink and gold",
  "model": "@cf/black-forest-labs/flux-1-schnell"
}
```

`model` is optional — defaults to `@cf/black-forest-labs/flux-1-schnell`.

**Success response**

```json
{
  "success": true,
  "image": "data:image/png;base64,…",
  "provider": "cloudflare"
}
```

**Error response**

```json
{
  "success": false,
  "error": {
    "code": "IMAGE_GENERATION_FAILED",
    "message": "Unable to generate the fashion design. Please try again."
  }
}
```

---

### `POST /api/try-on`

AI Virtual Try-On via IDM-VTON (Hugging Face Space).

**Request** (`multipart/form-data`)

| Field | Type | Description |
|---|---|---|
| `person` | file | Full-body photo of the user |
| `garment` | file | Clothing item image |
| `garment_description` | string (optional) | Text description of the garment — improves quality |

**Success response**

```json
{
  "success": true,
  "image": "data:image/jpeg;base64,…"
}
```

---

### `GET /api/products/search`

Search and rank H&M products matching a design specification.

**Query parameters**

| Parameter | Type | Description |
|---|---|---|
| `query` | string (required) | Search query (min 2 chars) |
| `category` | string | Optional category hint |
| `color` | string | Optional color hint |
| `budget` | float | Max price in INR |
| `limit` | int | Results to return (1–10, default 5) |

**Example request**

```
GET /api/products/search?query=black+cotton+shirt&category=shirt&color=black&budget=2500&limit=5
```

**Success response**

```json
{
  "success": true,
  "products": [
    {
      "name": "H&M Cotton Shirt",
      "brand": "H&M",
      "price": 1999.0,
      "currency": "INR",
      "image": "https://lp2.hm.com/…",
      "url": "https://www2.hm.com/en_in/productpage.123.html",
      "category": "Tops",
      "rating": null,
      "source": "H&M",
      "recommendation_score": 91
    }
  ],
  "query": "black cotton shirt",
  "source": "H&M via RapidAPI"
}
```

---

### `GET /api/health`

Returns configuration status for all integrated providers.

```json
{
  "status": "ok",
  "providers": {
    "cloudflare": { "configured": true },
    "idm_vton":   { "configured": true, "space": "yisol/IDM-VTON" },
    "rapidapi":   { "configured": true }
  }
}
```

---

### `GET /api/models`

Returns the list of supported image generation models.

```json
{
  "default": "@cf/black-forest-labs/flux-1-schnell",
  "models": [
    { "id": "@cf/black-forest-labs/flux-1-schnell",         "label": "flux-1-schnell" },
    { "id": "@cf/bytedance/stable-diffusion-xl-lightning",  "label": "stable-diffusion-xl-lightning" },
    { "id": "@cf/lykon/dreamshaper-8-lcm",                  "label": "dreamshaper-8-lcm" },
    { "id": "@cf/stabilityai/stable-diffusion-xl-base-1.0", "label": "stable-diffusion-xl-base-1.0" }
  ]
}
```

---

## Security

- `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, and `RAPIDAPI_KEY` are loaded exclusively from the server-side `.env` — they are never returned in API responses, logged, or included in error messages.
- Raw upstream error bodies from Cloudflare and Hugging Face are sanitized before reaching the client.
- CORS is an explicit allow-list — no wildcard `*` in production.
- File uploads (virtual try-on) are validated before forwarding.
- Rate limiting is enforced per IP via `slowapi` (60 requests / minute default).
- `.env` is in `.gitignore` and has never been committed. Only `.env.example` (with placeholder values) is tracked.

For full details see [README-API-SETUP.md](README-API-SETUP.md).

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Tests cover:

1. Backend starts correctly
2. `/api/health` returns expected structure
3. Input validation (prompt too short)
4. Missing credentials → safe 503 (no token leaked)
5. Cloudflare errors are sanitized before reaching the client
6. Successful generation returns `data:image/png;base64,…`
7. Credentials never appear in any response

All tests are **fully mocked** — no real API calls or credits are consumed.

---

## Example Prompts

```
Modern Indian half-saree in pastel pink and gold

Royal Rajasthani bandhani kurta — indigo with gold block print

Oversized linen co-ord set in soft terracotta

Contemporary silk saree with geometric motif border

Minimalist black cotton kurta with white embroidery under ₹3000

Cyberpunk streetwear jacket with neon accents
```

---

## Engineering Challenges

| Challenge | Approach |
|---|---|
| **AI generation latency** | Backend integration with async FastAPI + client-side loading states and error recovery |
| **Third-party API credential security** | All keys loaded via server-side environment variables; CORS allow-list prevents cross-origin abuse |
| **Virtual try-on reliability** | Input validation on file type and size before forwarding; structured error codes returned to the client |
| **Product matching accuracy** | Weighted scoring algorithm (category 40%, color 25%, budget 20%, style 15%) applied to RapidAPI metadata |
| **Multi-model image generation** | Pydantic allowlist validates model IDs server-side to prevent prompt injection via model field |

---

## Future Roadmap

- [ ] Advanced garment extraction for improved segmentation
- [ ] Higher-fidelity virtual try-on pipeline
- [ ] Additional fashion marketplace integrations
- [ ] User authentication and cloud-based collections
- [ ] Personalized recommendations based on style history
- [ ] Mobile application
- [ ] Advanced usage analytics

---

## Project Status

🟢 **Active Internship Project**

```
Version  : v2.0.0
Status   : Functional prototype — IBM Internship 2026 submission
API      : AI Fashion Studio API v2.0.0
```

---

<div align="center">

## Built By

### Piyush Ramteke

AI · ML · Data Science · Python

[GitHub →](https://github.com/Piyu242005)

*IBM Internship 2026*

</div>

---

## License

This project is licensed under the **MIT License** — free for personal, educational, and commercial use.

**Third-party component notice:**
The virtual try-on feature integrates [IDM-VTON](https://github.com/yisol/IDM-VTON), which is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (non-commercial). Use of the virtual try-on feature is subject to IDM-VTON's license terms.

---

<div align="center">

### AI Fashion Design Generator

**Built with React · FastAPI · Cloudflare Workers AI · Google Gemini · IDM-VTON**

⭐ Star this repository if you found it useful.

</div>
