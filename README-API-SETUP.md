# AI Fashion Studio — Setup Guide

## Architecture

```
Browser (React + Vite)
    │
    ├─ Spec extraction  ──► Gemini 2.5 Flash (free tier)  [client-side]
    │
    └─ HTTP calls
            │
            ▼
       FastAPI backend (port 8000)  —OR—  Vercel serverless functions
            │
            ├─ Image generation  ──► Cloudflare Workers AI → FLUX / SDXL
            ├─ Product search    ──► RapidAPI H&M Store
            └─ Virtual try-on   ──► Hugging Face IDM-VTON (gradio_client)
```

**Your API tokens never reach the browser.** They live only in the server-side `.env` file.

---

## Cloudflare Workers AI Setup

### 1. Create a Cloudflare account
Sign up at https://dash.cloudflare.com (free).

### 2. Enable Workers AI
In the dashboard: **AI → Workers AI** → click "Enable".

### 3. Get your Account ID
Your Account ID is shown in the **right sidebar** of any Cloudflare dashboard page (labelled "Account ID").

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

> ⚠️ Use placeholder values only in `.env.example` and this README.
> Never put a real token in source code, Git history, or any committed file.

---

## Google Gemini Setup (optional — for spec extraction)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Add to `.env`:

```env
VITE_GEMINI_API_KEY=your_gemini_key_here
```

Without this key the app uses a local mock spec — image generation still works.

---

## Running the Project

### Prerequisites
- Node.js 18+
- Python 3.10+

### Step 1 — Install frontend dependencies

```bash
npm install
```

### Step 2 — Set up the Python backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Start the FastAPI backend

```bash
# From the backend/ directory, with venv activated
uvicorn app.main:app --reload --port 8000
```

Verify at: http://localhost:8000/api/health

Expected response:
```json
{
  "status": "ok",
  "providers": {
    "cloudflare": { "configured": true },
    "idm_vton":   { "configured": false, "space": "yisol/IDM-VTON" },
    "rapidapi":   { "configured": false }
  }
}
```

### Step 4 — Start the React frontend

In a **new terminal** (keep the backend running):

```bash
npm run dev
```

Open http://localhost:5173

### Step 5 — Generate a fashion design

1. Click **Studio** in the navigation
2. Type a prompt, e.g.:
   - `Modern Indian half-saree in pastel pink and gold`
   - `Luxury men's beach resort suit in linen`
   - `Contemporary cotton kurta with geometric patterns under Rs 3000`
3. Click **Generate Design**
4. The request flows: React → FastAPI → Cloudflare FLUX.1 → FastAPI → React

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

All 7 tests run with mocked Cloudflare responses — no real API calls or credits used.

---

## API Reference

### `POST /api/design`  ← Primary (Cloudflare)

```json
// Request
{ "prompt": "Modern Indian half-saree in pastel pink and gold" }

// Success
{ "success": true, "image": "data:image/png;base64,...", "provider": "cloudflare" }

// Error
{ "success": false, "error": { "code": "IMAGE_GENERATION_FAILED", "message": "..." } }
```

### `GET /api/health`

```json
{
  "status": "ok",
  "providers": {
    "cloudflare": { "configured": true },
    "idm_vton":   { "configured": false, "space": "yisol/IDM-VTON" },
    "rapidapi":   { "configured": false }
  }
}
```

---

## Free Tier Limits

| Provider | Free Allowance | Notes |
|---|---|---|
| Cloudflare Workers AI | Generous free tier (10,000 neurons/day) | Required for image generation |
| Google Gemini | Free tier for text generation | Spec extraction only |
| Hugging Face IDM-VTON | ZeroGPU quota (~2 GPU-min/day unauthenticated) | HF_TOKEN increases quota |
| RapidAPI H&M Store | Free tier available | Required for product recommendations |

---

## Security

- `CLOUDFLARE_API_TOKEN`, `HF_TOKEN`, and `RAPIDAPI_KEY` live only in the server-side `.env` — never in browser code
- `CLOUDFLARE_ACCOUNT_ID` is also server-side only
- Raw upstream errors (Cloudflare, HuggingFace, RapidAPI) are sanitised before being sent to the client
- No credentials appear in logs, error responses, or the frontend bundle
- `.env` is listed in `.gitignore` and has never been committed
