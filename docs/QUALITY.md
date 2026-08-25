# Engineering Quality

## Current quality gates

The repository now has automated checks for:

1. Frontend production build with Vite.
2. Python API contract tests with pytest.
3. Coverage reporting for backend modules.
4. Environment-template secret hygiene.
5. `.env` ignore verification.

The CI workflow runs on pushes and pull requests targeting `main`.

## Local verification

```bash
npm ci
python -m pip install -r api/requirements.txt
python -m pip install -r requirements-dev.txt
npm run build
npm test
```

## Production hardening roadmap

- Move the remaining legacy client-side Gemini call in `src/App.jsx` to `/api/gemini`.
- Add per-IP/user rate limiting to expensive generation endpoints.
- Add request IDs and provider latency telemetry.
- Persist generation metrics for model comparison.
- Add visual regression tests for the main studio workflow.
- Add an authenticated analytics/admin view.

These items are intentionally listed as roadmap work rather than represented as completed features.
