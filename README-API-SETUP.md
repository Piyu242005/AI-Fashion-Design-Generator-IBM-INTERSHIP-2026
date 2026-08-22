# AI Fashion Studio — API Setup Guide

## Architecture

```text
Browser (React + Vite)
        │
        ├─ Spec extraction  ──► /api/gemini
        │                         │
        │                         └─► Google Gemini 2.5 Flash
        │
        └─ HTTP calls (relative /api/…)
                │
                ▼
           Vercel Python Serverless Functions
                │
                ├── api/design.py    ──► Cloudflare Workers AI (FLUX / SDXL)
                ├── api/gemini.py    ──► Google Gemini (fashion spec extraction)
                ├── api/products.py  ──► RapidAPI H&M Store
                ├── api/try-on.py    ──► Hugging Face IDM-VTON
                └── api/health.py    ──► health check
```

**All API tokens are server-side only.** `CLOUDFLARE_API_TOKEN`, `GEMINI_API_KEY`, `HF_TOKEN`, and `RAPIDAPI_KEY` must live only in Vercel/server environment variables. Never prefix these secrets with `VITE_`.

---

## Cloudflare Workers AI Setup

### 1. Create a Cloudflare account
Sign up at https://dash.cloudflare.com.

### 2. Enable Workers AI
In the dashboard: **AI → Workers AI** → enable the service.

### 3. Get your Account ID
Your Account ID is shown in the Cloudflare dashboard sidebar.

### 4. Create an API token
Create a custom token with the Workers AI permissions required by your account.

### 5. Add credentials

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
```

---

## Google Gemini Setup

1. Go to https://aistudio.google.com/app/apikey
2. Create an API key.
3. Store it server-side:

```env
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The browser calls `POST /api/gemini`; the Gemini credential is read only by `api/gemini.py` and is never intentionally exposed to the client bundle.

---

## Hugging Face IDM-VTON Setup

1. Sign up at https://huggingface.co
2. Create a READ token at https://huggingface.co/settings/tokens
3. Add:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_SPACE_ID=yisol/IDM-VTON
```

The token must remain server-side.

---

## RapidAPI H&M Store Setup

1. Sign up at https://rapidapi.com
2. Subscribe to the H&M Store API.
3. Add:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=apidojo-hm-hennes-mauritz-v1.p.rapidapi.com
```

---

## Running the Project

### Prerequisites
- Node.js 18+
- Vercel CLI. The project can also launch it through `npx` automatically.

### Step 1 — Install dependencies

```bash
npm install
```

### Step 2 — Configure environment

```bash
cp .env.example .env
# Fill in the server-side credentials
```

### Step 3 — Start local development

```bash
npm run dev
```

The `dev` script uses `npx vercel dev`, so the React app and Python serverless functions run through the same local Vercel runtime.

Open http://localhost:3000.

### Step 4 — Verify the API

```text
GET http://localhost:3000/api/health
```

Expected response:

```json
{ "status": "ok", "service": "ai-fashion-design-generator", "cloudflare_ready": true }
```

---

## API Reference

### `POST /api/gemini` — Fashion specification extraction

```json
{ "prompt": "Modern Indian half-saree in pastel pink and gold" }
```

Success:

```json
{
  "success": true,
  "specification": {
    "category": "",
    "fabric": "",
    "colors": [],
    "sustainability_score": 0,
    "budget": { "maximum": 0 },
    "garment_description": ""
  }
}
```

### `POST /api/design` — Image generation

```json
{ "prompt": "Modern Indian half-saree in pastel pink and gold" }
```

### `GET /api/products/search` — H&M recommendations

```text
GET /api/products/search?query=cotton+kurta&category=tops&budget=3000&limit=5
```

### `POST /api/try-on` — Virtual try-on

Multipart form fields:
- `person` — person image
- `garment` — garment image
- `garment_description` — optional text

### `GET /api/health` — Health check

```json
{ "status": "ok", "service": "ai-fashion-design-generator", "cloudflare_ready": true }
```

---

## Production Deployment

```bash
vercel --prod
```

Set these environment variables in **Vercel → Project → Settings → Environment Variables**:

| Variable | Purpose |
|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Workers AI |
| `GEMINI_API_KEY` | Gemini server-side API key |
| `GEMINI_MODEL` | Gemini model name |
| `HF_TOKEN` | Hugging Face access |
| `HF_SPACE_ID` | IDM-VTON Space ID |
| `RAPIDAPI_KEY` | RapidAPI authentication |
| `RAPIDAPI_HOST` | RapidAPI host |

---

## Security Notes

- No Gemini, Cloudflare, Hugging Face, or RapidAPI secret should use a `VITE_` prefix.
- `.env` must never be committed.
- The frontend uses relative `/api/...` requests only.
- API errors are sanitised before being returned to the browser.
- Keep the production frontend/API domain as the only trusted origin when you later tighten CORS policy.
