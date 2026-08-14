# ✂️ AI Fashion Design Generator

> **IBM Internship 2026 — Final Submission**
> Built by [Piyush Ramteke](https://github.com/Piyu242005)

Transform fashion ideas into AI-generated designs, product recommendations, and virtual try-on — all on a single Vercel deployment.

---

## Deployment Architecture

```
Browser (React + Vite)
        │
        ├─ Gemini 2.5 Flash ──► Fashion Spec Extraction  [client-side]
        │
        └─ HTTP calls (relative /api/…)
                │
                ▼
           Vercel
            ├── React frontend  (static, CDN)
            └── Python Serverless API
                    ├── api/design.py     POST /api/design
                    │        └──► Cloudflare Workers AI  (FLUX / SDXL)
                    ├── api/products.py   GET  /api/products/search
                    │        └──► RapidAPI H&M Store
                    ├── api/try-on.py     POST /api/try-on
                    │        └──► Hugging Face IDM-VTON
                    └── api/health.py     GET  /api/health
```

**All API secrets stay server-side.** `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, and `RAPIDAPI_KEY` never reach the browser.

---

## Core Features

| Feature | Description |
|---|---|
| 🎨 AI Fashion Design | Generate fashion images from text prompts via Cloudflare Workers AI |
| 🧠 Gemini Spec Extraction | Parse prompts into structured fashion specifications |
| 👗 4 AI Models | FLUX.1-schnell, SDXL Base 1.0, DreamShaper 8, SDXL Lightning |
| 🛍️ Product Recommendations | Real H&M products via RapidAPI with recommendation scoring |
| 👗 Virtual Try-On | AI try-on via Hugging Face IDM-VTON (gradio_client) |
| ↔️ Before/After | Side-by-side person vs try-on result |
| 💾 Collections | Save, track, remix, and download generated designs |
| 📦 Tech Pack | Export full garment specification |
| 🖼️ Garment Gallery | 100 open-source garment samples with category filters |
| 👥 Model Gallery | 50 female + 20 male model photos |

---

## Project Structure

```
AI-Fashion-Design-Generator-IBM-INTERSHIP-2026/
│
├── src/
│   └── App.jsx              # React frontend (all UI)
│
├── api/
│   ├── design.py            # POST /api/design  → Cloudflare Workers AI
│   ├── products.py          # GET  /api/products/search  → RapidAPI H&M
│   ├── try-on.py            # POST /api/try-on  → Hugging Face IDM-VTON
│   ├── health.py            # GET  /api/health
│   └── requirements.txt     # Python deps for serverless functions
│
├── public/
│   └── samples/             # Local garment sample images
│
├── samples/                 # Source copies of garment samples
│
├── package.json             # Node dependencies + build scripts
├── vercel.json              # Vercel routing + function timeouts
├── .env.example             # Environment variable template
├── README.md
├── README-API-SETUP.md
├── LICENSE.md
├── SECURITY.md
└── CODE_OF_CONDUCT.md
```

---

## Quick Start

### Prerequisites

- Node.js 18+
- [Vercel CLI](https://vercel.com/docs/cli): `npm i -g vercel`

### 1. Clone & install

```bash
git clone https://github.com/Piyu242005/AI-Fashion-Design-Generator-IBM-INTERSHIP-2026.git
cd AI-Fashion-Design-Generator-IBM-INTERSHIP-2026
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials (see [API Setup](#environment-variables) below).

### 3. Run locally

```bash
vercel dev
```

Open http://localhost:3000

> `vercel dev` runs both the React frontend and all Python serverless functions locally,
> mirroring the production environment exactly. No separate backend process needed.

### 4. Deploy to production

```bash
vercel --prod
```

Set the same environment variables in the Vercel dashboard under **Project → Settings → Environment Variables**.

---

## Environment Variables

### Browser-visible (safe to expose)

| Variable | Required | Description |
|---|---|---|
| `VITE_GEMINI_API_KEY` | Yes | Google Gemini API key for spec extraction |
| `VITE_GEMINI_MODEL` | No | Gemini model ID (default: `gemini-2.5-flash`) |

### Server-only (never in browser bundle)

| Variable | Required | Description |
|---|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | Yes | Cloudflare account ID |
| `CLOUDFLARE_API_TOKEN` | Yes | Cloudflare Workers AI API token |
| `HF_TOKEN` | Recommended | Hugging Face READ token (higher ZeroGPU quota) |
| `HF_SPACE_ID` | No | IDM-VTON space (default: `yisol/IDM-VTON`) |
| `RAPIDAPI_KEY` | Yes | RapidAPI key for H&M product search |
| `RAPIDAPI_HOST` | No | RapidAPI host (default: `apidojo-hm-hennes-mauritz-v1.p.rapidapi.com`) |

**Never use `VITE_` prefix on `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, or `RAPIDAPI_KEY`.**

---

## API Reference

### `POST /api/design`

Generate a fashion design image.

```json
// Request
{ "prompt": "Modern Indian half-saree in pastel pink and gold", "model": "@cf/black-forest-labs/flux-1-schnell" }

// Success
{ "success": true, "image": "data:image/png;base64,…" }

// Error
{ "success": false, "error": { "code": "IMAGE_GENERATION_FAILED", "message": "…" } }
```

**Supported models:**

| Model ID | Label |
|---|---|
| `@cf/black-forest-labs/flux-1-schnell` | FLUX.1-schnell *(default)* |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | SDXL Base 1.0 |
| `@cf/lykon/dreamshaper-8-lcm` | DreamShaper 8 |
| `@cf/bytedance/stable-diffusion-xl-lightning` | SDXL Lightning |

---

### `GET /api/products/search`

Search H&M products via RapidAPI.

```
GET /api/products/search?query=cotton+kurta&category=tops&color=blue&budget=3000&limit=5
```

```json
// Success
{
  "success": true,
  "products": [
    {
      "name": "Cotton Blend Shirt",
      "brand": "H&M",
      "price": 1299.0,
      "currency": "INR",
      "image": "https://…",
      "url": "https://www2.hm.com/…",
      "category": "Tops",
      "recommendation_score": 85
    }
  ],
  "query": "cotton kurta",
  "source": "H&M via RapidAPI"
}
```

---

### `POST /api/try-on`

Virtual try-on via IDM-VTON. Accepts `multipart/form-data`.

| Field | Type | Required | Notes |
|---|---|---|---|
| `person` | file | Yes | Full-body photo, JPEG/PNG/WebP, ≤ 10 MB |
| `garment` | file | Yes | Garment image, JPEG/PNG/WebP, ≤ 10 MB |
| `garment_description` | text | No | Short description improves quality |

```json
// Success
{ "success": true, "image": "data:image/jpeg;base64,…", "provider": "idm-vton" }

// Error
{ "success": false, "error": { "code": "SPACE_LOADING", "message": "IDM-VTON is waking up. Wait 30 s and retry." } }
```

| Error code | HTTP | Meaning |
|---|---|---|
| `MISSING_FILES` | 400 | person or garment not provided |
| `FILE_TOO_LARGE` | 413 | image > 10 MB |
| `QUOTA_EXCEEDED` | 429 | ZeroGPU daily quota reached |
| `SPACE_LOADING` | 503 | Space is cold-starting |
| `TIMEOUT` | 504 | GPU queue busy |

---

### `GET /api/health`

```json
{ "status": "ok", "service": "ai-fashion-design-generator", "cloudflare_ready": true }
```

---

## Supported AI Models

| Provider | Model | Strength |
|---|---|---|
| Cloudflare Workers AI | FLUX.1-schnell | Fast, photorealistic |
| Cloudflare Workers AI | SDXL Base 1.0 | High detail |
| Cloudflare Workers AI | DreamShaper 8 LCM | Creative/artistic |
| Cloudflare Workers AI | SDXL Lightning | Ultra-fast (4 steps) |
| Google Gemini | gemini-2.5-flash | Fashion spec extraction |
| Hugging Face | IDM-VTON | Virtual try-on |

---

## Free Tier Limits

| Provider | Free Allowance |
|---|---|
| Cloudflare Workers AI | 10,000 neurons/day |
| Google Gemini | Free tier for `gemini-2.5-flash` |
| Hugging Face ZeroGPU | ~2 GPU-min/day unauthenticated; more with `HF_TOKEN` |
| RapidAPI H&M | Free tier available |

---

## Security

- `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, `RAPIDAPI_KEY` live only in Vercel environment variables — never in the browser bundle
- Raw upstream errors are sanitised before being returned to the client — no credentials, account IDs, or internal stack traces leak
- All uploaded images are size-capped at 10 MB and processed in-memory (temporary files cleaned up automatically)
- `.env` is listed in `.gitignore` and has never been committed

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Tailwind CSS 4, Lucide React |
| Serverless API | Python 3, Vercel serverless functions |
| Image Generation | Cloudflare Workers AI (FLUX / SDXL) |
| Fashion Spec | Google Gemini 2.5 Flash |
| Product Search | RapidAPI H&M Store |
| Virtual Try-On | Hugging Face IDM-VTON (gradio_client) |
| Hosting | Vercel |

---

## Screenshots

### Dashboard — Runway & Trending Concepts
![Dashboard](public/screenshots/DASHBOARD.jpeg)

### Studio — Generated Design Output
![Studio](public/screenshots/generated-output.png)

---

## Example Prompts

- `Modern Indian half-saree in pastel pink and gold`
- `Luxury men's beach resort suit in white linen`
- `Contemporary cotton kurta with geometric patterns under ₹3000`
- `Oversized blazer in camel wool with gold buttons, street style`
- `Silk lehenga in blush pink with intricate mirror work`

---

## Built By

### Piyush Ramteke
IBM Internship 2026
[GitHub](https://github.com/Piyu242005)

---

## License

### AI Fashion Design Generator
MIT License — see [LICENSE.md](LICENSE.md)

### IDM-VTON (Hugging Face Space)
CC BY-NC-SA 4.0 — non-commercial use only.
See: https://huggingface.co/spaces/yisol/IDM-VTON
