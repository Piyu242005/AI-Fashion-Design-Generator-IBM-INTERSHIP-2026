# AI Fashion Studio — API Setup Guide

## Architecture

```
Browser (React + Vite)
        │
        ├─ Spec extraction  ──► Gemini 2.5 Flash  [client-side]
        │
        └─ HTTP calls (relative /api/…)
                │
                ▼
           Vercel Python Serverless Functions
                │
                ├── api/design.py    ──► Cloudflare Workers AI (FLUX / SDXL)
                ├── api/products.py  ──► RapidAPI H&M Store
                ├── api/try-on.py    ──► Hugging Face IDM-VTON
                └── api/health.py    ──► health check
```

**Your API tokens never reach the browser.** `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, and `RAPIDAPI_KEY` live only in Vercel environment variables.

---

## Cloudflare Workers AI Setup

### 1. Create a Cloudflare account
Sign up at https://dash.cloudflare.com (free).

### 2. Enable Workers AI
In the dashboard: **AI → Workers AI** → click "Enable".

### 3. Get your Account ID
Your Account ID is shown in the **right sidebar** of any Cloudflare dashboard page.

### 4. Create an API token
1. Go to **My Profile → API Tokens → Create Token**
2. Use "Create Custom Token"
3. Add permissions:
   - **Workers AI** — Read
   - **Workers AI** — Edit
4. Click "Continue to summary" → "Create Token"
5. Copy the token **now** — it is shown only once.

### 5. Add credentials to `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
```

> ⚠️ Never put a real token in source code, Git history, or any committed file.

---

## Google Gemini Setup

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Add to `.env`:

```env
VITE_GEMINI_API_KEY=your_gemini_key_here
```

The `VITE_` prefix makes this key available in the browser bundle. Use a free-tier key with limited scope only. Without this key the app uses a local mock spec — image generation still works.

---

## Hugging Face IDM-VTON Setup

1. Sign up at https://huggingface.co
2. Go to https://huggingface.co/settings/tokens
3. Create a token with **READ** permission
4. Add to `.env`:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Never prefix with `VITE_` — this key must never reach the browser.

Without `HF_TOKEN` the app falls back to unauthenticated quota (~2 GPU-min/day on ZeroGPU).

---

## RapidAPI H&M Store Setup

1. Sign up at https://rapidapi.com
2. Search for "H&M Store" → subscribe (free tier available)
3. Copy your API key from the RapidAPI dashboard
4. Add to `.env`:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=apidojo-hm-hennes-mauritz-v1.p.rapidapi.com
```

> ⚠️ Never prefix with `VITE_` — this key must never reach the browser.

---

## Running the Project

### Prerequisites
- Node.js 18+
- [Vercel CLI](https://vercel.com/docs/cli): `npm i -g vercel`

### Step 1 — Install frontend dependencies

```bash
npm install
```

### Step 2 — Configure environment

```bash
cp .env.example .env
# Fill in your credentials
```

### Step 3 — Start local development server

```bash
vercel dev
```

Open http://localhost:3000

This runs both the React frontend and all Python serverless functions locally. No separate backend process needed.

### Step 4 — Verify health endpoint

```
GET http://localhost:3000/api/health
```

Expected response:
```json
{ "status": "ok", "service": "ai-fashion-design-generator", "cloudflare_ready": true }
```

### Step 5 — Generate a fashion design

1. Click **Studio** in the navigation
2. Type a prompt, e.g.:
   - `Modern Indian half-saree in pastel pink and gold`
   - `Luxury men's beach resort suit in linen`
   - `Contemporary cotton kurta with geometric patterns under ₹3000`
3. Click **Generate Design**
4. The request flows: React → `/api/design` (Vercel serverless) → Cloudflare Workers AI → response

---

## Deploying to Production

```bash
vercel --prod
```

Set all environment variables in the Vercel dashboard under **Project → Settings → Environment Variables**:

| Variable | Where |
|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | Vercel env vars |
| `CLOUDFLARE_API_TOKEN` | Vercel env vars |
| `VITE_GEMINI_API_KEY` | Vercel env vars |
| `VITE_GEMINI_MODEL` | Vercel env vars |
| `HF_TOKEN` | Vercel env vars |
| `HF_SPACE_ID` | Vercel env vars (optional) |
| `RAPIDAPI_KEY` | Vercel env vars |
| `RAPIDAPI_HOST` | Vercel env vars (optional) |

---

## API Reference

### `POST /api/design`  ← Image generation

```json
// Request
{ "prompt": "Modern Indian half-saree in pastel pink and gold" }

// Success
{ "success": true, "image": "data:image/png;base64,...", "provider": "cloudflare" }

// Error
{ "success": false, "error": { "code": "IMAGE_GENERATION_FAILED", "message": "..." } }
```

### `GET /api/products/search`  ← H&M product recommendations

```
GET /api/products/search?query=cotton+kurta&category=tops&budget=3000&limit=5
```

### `POST /api/try-on`  ← Virtual try-on

Multipart form with `person` (image), `garment` (image), `garment_description` (optional text).

### `GET /api/health`  ← Status check

```json
{ "status": "ok", "service": "ai-fashion-design-generator", "cloudflare_ready": true }
```

---

## Free Tier Limits

| Provider | Free Allowance | Notes |
|---|---|---|
| Cloudflare Workers AI | 10,000 neurons/day | Required for image generation |
| Google Gemini | Free tier for text generation | Spec extraction only |
| Hugging Face IDM-VTON | ZeroGPU quota (~2 GPU-min/day unauthenticated) | `HF_TOKEN` increases quota |
| RapidAPI H&M Store | Free tier available | Required for product recommendations |

---

## Security

- `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, and `RAPIDAPI_KEY` live only in Vercel environment variables — never in browser code
- Raw upstream errors (Cloudflare, HuggingFace, RapidAPI) are sanitised before being sent to the client
- No credentials appear in logs, error responses, or the frontend bundle
- `.env` is listed in `.gitignore` and has never been committed
