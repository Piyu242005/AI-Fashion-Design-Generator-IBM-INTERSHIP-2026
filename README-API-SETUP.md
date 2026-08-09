# AI Fashion Studio — API Setup Guide

## Architecture Overview

```
Browser (React + Vite)
    │
    ├─ Text / Spec extraction ──► Gemini 2.5 Flash (free)   [client-side]
    │
    └─ Image generation ─────────► FastAPI backend
                                        │
                                        └──► Hugging Face FLUX.1 (free credits)
                                                  ↓ (credits exhausted)
                                             Unsplash placeholder (fallback)
```

Your **HuggingFace API token is never exposed to the browser** — it lives only in the
Python backend's `.env` file.

---

## Step 1 — Clone & install frontend

```bash
# Install frontend deps (Vite + Tailwind + lucide-react)
npm install

# Install Vite + React if not already present
npm install vite @vitejs/plugin-react react react-dom
```

---

## Step 2 — Configure environment variables

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and fill in **two** values:

| Variable | Where to get it | Free? |
|---|---|---|
| `VITE_GEMINI_API_KEY` | https://aistudio.google.com/app/apikey | ✅ Free tier |
| `HUGGINGFACE_API_TOKEN` | https://huggingface.co/settings/tokens | ✅ $0.10 credits |

Leave everything else as-is for local development.

---

## Step 3 — Start the Python backend

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

Verify it's running:
```
http://localhost:8000/api/health
```
Expected response:
```json
{ "status": "ok", "hf_token_set": true, "model": "black-forest-labs/FLUX.1-schnell" }
```

---

## Step 4 — Start the React frontend

In a **separate terminal** (keep the backend running):

```bash
# Back in the project root
npm run dev
```

Open http://localhost:5173 in your browser.

---

## Free Tier Limits

| Provider | Free Allowance | Best For |
|---|---|---|
| Google Gemini | Generous free tier (text) | Fashion spec extraction |
| HuggingFace | $0.10/month inference credits | Dev & demo image generation |
| Unsplash (fallback) | Unlimited | Offline / no-credit fallback |

### When HuggingFace credits run out
The backend returns a `402` error and the frontend automatically falls back to an
Unsplash placeholder — **the app never crashes**.

### Upgrading to production
1. Replace `HUGGINGFACE_API_TOKEN` with a paid-tier token, or
2. Switch to **fal.ai** by adding a `/api/generate-image-fal` route in `backend/main.py`, or
3. Use **Google Imagen 4.0** (paid) by re-enabling the Imagen route.

---

## Model Options (HuggingFace)

Change `HUGGINGFACE_IMAGE_MODEL` in `.env`:

| Model | Speed | Quality | Steps |
|---|---|---|---|
| `black-forest-labs/FLUX.1-schnell` | ⚡ Fast | Good | 1–4 |
| `black-forest-labs/FLUX.1-dev` | Medium | Excellent | 20–50 |
| `stabilityai/stable-diffusion-xl-base-1.0` | Medium | Good | 20–40 |

For a **college project / demo**, `FLUX.1-schnell` at 4 steps is the sweet spot.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `CORS error` in browser console | Make sure FastAPI backend is running on port 8000 |
| `503 Model is loading` | Wait 20–30 s and retry — HF cold-starts free-tier models |
| `402 Credits exhausted` | Add HF billing or use Unsplash fallback mode (remove token) |
| `VITE_GEMINI_API_KEY not found` | Restart `npm run dev` after editing `.env` |
| Gemini returns mock spec | Check `VITE_GEMINI_API_KEY` is set and prefixed with `VITE_` |
