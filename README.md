# ✂️ AI Fashion Design Generator

> **IBM Internship 2026 — Final Submission**  
> Built by **Piyush Ramteke**

Transform fashion ideas into AI-generated designs, structured fashion specifications, product recommendations, and virtual try-on from one production-oriented web application.

## 🚀 Highlights

- 🎨 Text-to-fashion image generation with **4 Cloudflare Workers AI models**
- 🧠 Structured fashion-spec extraction with **Gemini 2.5 Flash**
- 👗 AI virtual try-on with **IDM-VTON**
- 🛍️ Real H&M product recommendations with scoring
- 📦 Fashion tech-pack generation
- 💾 Local design collections, remixing, tracking, and downloads
- 🧪 Automated API contract tests
- ⚙️ GitHub Actions CI for frontend build + backend tests
- 🩺 Health/readiness endpoint for upstream services
- 📊 Documented model-evaluation methodology and engineering quality standards

---

## 🏗️ Deployment Architecture

```text
Browser (React + Vite)
        │
        │ relative /api/* requests
        ▼
      Vercel
        ├── React frontend (static/CDN)
        └── Python Serverless API
              ├── /api/gemini       → Google Gemini 2.5 Flash
              ├── /api/design       → Cloudflare Workers AI
              │                         ├─ FLUX.1 Schnell
              │                         ├─ SDXL Base
              │                         ├─ DreamShaper 8
              │                         └─ SDXL Lightning
              ├── /api/products     → RapidAPI H&M
              ├── /api/try-on       → Hugging Face IDM-VTON
              └── /api/health       → readiness/status

GitHub Actions
        ├── Frontend build
        └── Python API tests + coverage
```

**API credentials are server-side only.** Gemini, Cloudflare, Hugging Face, and RapidAPI secrets are handled by the Python API layer rather than being embedded in the production frontend bundle.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| 🎨 AI Fashion Design | Generate fashion images from text prompts |
| 🧠 Fashion Intelligence | Convert natural-language prompts into structured fashion specs |
| 🤖 Multi-Model Generation | FLUX, SDXL Base, DreamShaper, and SDXL Lightning |
| 🛍️ Product Recommendations | Search real H&M products with category, color, and budget filters |
| 👗 Virtual Try-On | Apply garments to a person image with IDM-VTON |
| ↔️ Before / After | Compare original and try-on results |
| 💾 Collections | Save, track, remix, delete, and download designs |
| 📦 Tech Pack | Export structured garment specifications |
| 🖼️ Garment Gallery | Curated garment samples with category filters |
| 👥 Model Gallery | Female and male model samples for try-on workflows |
| 🩺 Health Check | Inspect server-side provider readiness without exposing secrets |

---

## 📁 Project Structure

```text
AI-Fashion-Design-Generator-IBM-INTERSHIP-2026/
│
├── src/
│   └── App.jsx
│
├── api/
│   ├── design.py
│   ├── gemini.py
│   ├── products.py
│   ├── try-on.py
│   ├── health.py
│   └── requirements.txt
│
├── tests/
│   └── test_api_contracts.py
│
├── docs/
│   ├── MODEL-EVALUATION.md
│   └── QUALITY.md
│
├── .github/workflows/
│   └── ci.yml
│
├── public/samples/
├── samples/
├── package.json
├── requirements-dev.txt
├── vercel.json
├── .env.example
├── SECURITY.md
├── LICENSE.md
└── README.md
```

> The frontend remains intentionally compact for the internship submission; backend responsibilities are separated into independently testable serverless endpoints.

---

## ⚡ Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Vercel CLI

```bash
npm install
```

Create `.env` from `.env.example` and configure the required server-side credentials.

### Run locally

```bash
npm run dev
```

This runs the Vercel development environment so the React frontend and Python serverless APIs can be exercised together.

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Coverage

```bash
npm run test:coverage
```

### Combined CI check

```bash
npm run ci
```

### Deploy

```bash
vercel --prod
```

---

## 🔐 Environment Variables

All AI/provider credentials are **server-side**.

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Gemini fashion specification extraction |
| `GEMINI_MODEL` | No | Gemini model; defaults to `gemini-2.5-flash` |
| `CLOUDFLARE_ACCOUNT_ID` | Yes | Cloudflare Workers AI account |
| `CLOUDFLARE_API_TOKEN` | Yes | Cloudflare Workers AI authentication |
| `HF_TOKEN` | Recommended | Hugging Face authentication / quota |
| `HF_SPACE_ID` | No | IDM-VTON Space configuration |
| `RAPIDAPI_KEY` | Yes | H&M product API |
| `RAPIDAPI_HOST` | No | RapidAPI H&M host |

**Do not prefix provider secrets with `VITE_`.**

Never commit `.env` or real credentials.

---

## 🔌 API Reference

### `POST /api/gemini`

Extract structured fashion information from a natural-language prompt.

```json
{
  "prompt": "pastel pink linen summer dress under ₹3000"
}
```

Returns a normalized fashion specification such as category, fabric, colors, sustainability score, budget, and garment description.

### `POST /api/design`

Generate a fashion image.

```json
{
  "prompt": "Modern Indian half-saree in pastel pink and gold",
  "model": "@cf/black-forest-labs/flux-1-schnell"
}
```

Supported models:

| Model | Strength |
|---|---|
| FLUX.1 Schnell | Fast general-purpose generation |
| SDXL Base 1.0 | Detail |
| DreamShaper 8 LCM | Creative/artistic output |
| SDXL Lightning | Very fast generation |

### `GET /api/products/search`

Search and rank real H&M products.

```text
/api/products/search?query=cotton+kurta&category=tops&color=blue&budget=3000&limit=5
```

### `POST /api/try-on`

Accepts `multipart/form-data`:

| Field | Required | Limit |
|---|---|---|
| `person` | Yes | 10 MB |
| `garment` | Yes | 10 MB |
| `garment_description` | No | Short text |

The endpoint handles upload, GPU queue polling, timeout detection, provider errors, and temporary-file cleanup.

### `GET /api/health`

Returns non-secret service readiness information for configured providers.

---

## 🧪 Testing & Quality

The repository includes network-free automated tests for API contracts and parsing behavior.

Current checks include:

- Image-generation model allowlist
- Stable API error contracts
- Gemini JSON parsing
- Invalid Gemini response handling
- Health configuration checks
- Frontend production build

GitHub Actions runs the quality checks automatically on repository changes.

See:

- `docs/QUALITY.md` — engineering quality standards
- `docs/MODEL-EVALUATION.md` — reproducible AI model evaluation plan

---

## 📊 AI Evaluation

The project is designed to compare generation models using consistent prompts and measurable criteria:

| Metric | Purpose |
|---|---|
| Prompt adherence | Measures how closely output follows requested attributes |
| Visual quality | Human/structured quality assessment |
| Fashion detail | Garment structure, texture, and styling quality |
| Latency | End-to-end generation time |
| Reliability | Success/failure rate |
| Cost/usage | Provider resource efficiency |

The evaluation methodology is documented separately so benchmark results can be added without mixing experimental numbers with verified application behavior.

---

## 🩺 Production Readiness

The application includes:

- Server-side provider credentials
- Input validation
- Model allowlisting
- Upload size limits
- Sanitized upstream errors
- Explicit timeout handling
- Provider-specific error codes
- Health/readiness endpoint
- Automated API tests
- CI build/test checks

### Known limitations

- External AI providers can experience cold starts, quota limits, or transient failures.
- IDM-VTON quality depends on input image quality and provider GPU availability.
- Product availability and prices come from the external H&M API source and can change.
- Local collections currently use browser `localStorage` rather than a persistent database.

---

## 🧠 Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Tailwind CSS 4, Lucide React |
| API | Python 3, Vercel Serverless Functions |
| Fashion Intelligence | Google Gemini 2.5 Flash |
| Image Generation | Cloudflare Workers AI |
| Virtual Try-On | Hugging Face IDM-VTON |
| Product Search | RapidAPI H&M Store |
| Testing | Pytest, pytest-cov |
| CI | GitHub Actions |
| Hosting | Vercel |

---

## 🖼️ Screenshots

### Dashboard
![Dashboard](public/screenshots/DASHBOARD.jpeg)

### Studio — Generated Design
![Studio](public/screenshots/generated-output.png)

---

## 💡 Example Prompts

- `Modern Indian half-saree in pastel pink and gold`
- `Luxury men's beach resort suit in white linen`
- `Contemporary cotton kurta with geometric patterns under ₹3000`
- `Oversized blazer in camel wool with gold buttons, street style`
- `Silk lehenga in blush pink with intricate mirror work`

---

## 👨‍💻 Built By

**Piyush Ramteke**  
IBM Internship 2026

[GitHub](https://github.com/Piyu242005)

---

## 📄 License

The application is released under the MIT License; see `LICENSE.md`.

IDM-VTON is subject to its upstream **CC BY-NC-SA 4.0** license and should be treated as non-commercial unless the applicable licensing terms permit otherwise.
