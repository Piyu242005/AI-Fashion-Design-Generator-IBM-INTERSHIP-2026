"""
backend/tests/test_design.py
==============================
Unit tests for the POST /api/design endpoint.

All Cloudflare HTTP calls are mocked — no real API calls are made.
Tests verify:
  1. Backend starts and health check works.
  2. /api/health returns expected structure.
  3. /api/design validates input (prompt too short).
  4. Missing API credentials produce a safe 503 error (no token leaked).
  5. Cloudflare errors are handled safely (no raw error forwarded).
  6. Successful generation returns image data.
  7. API credentials never appear in any response body.
"""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── Import app after patching env so startup validation doesn't fail ─────────
import os
os.environ.setdefault("CLOUDFLARE_ACCOUNT_ID", "test_account_id")
os.environ.setdefault("CLOUDFLARE_API_TOKEN",  "test_secret_token_never_in_response")
os.environ.setdefault("HUGGINGFACE_API_TOKEN", "")

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ── Helpers ───────────────────────────────────────────────────────────────────
FAKE_B64   = base64.b64encode(b"fake-png-bytes").decode()
FAKE_DATA_URI = f"data:image/png;base64,{FAKE_B64}"
TEST_TOKEN    = "test_secret_token_never_in_response"
TEST_ACCOUNT  = "test_account_id"


def _response_contains_secret(body: str) -> bool:
    """Return True if any credential value appears in the response body."""
    return TEST_TOKEN in body or TEST_ACCOUNT in body


# ── Test 1: Backend starts ────────────────────────────────────────────────────
def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "AI Fashion Studio" in data["service"]


# ── Test 2: /api/health ───────────────────────────────────────────────────────
def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "cloudflare" in data["providers"]
    assert "idm_vton"   in data["providers"]   # key is idm_vton, not huggingface
    assert "rapidapi"   in data["providers"]
    # Credentials must NOT appear in health response
    assert not _response_contains_secret(resp.text)


# ── Test 3: Input validation — prompt too short ───────────────────────────────
def test_design_prompt_too_short(client):
    resp = client.post("/api/design", json={"prompt": "hi"})
    assert resp.status_code == 422   # Pydantic validation error
    # No credentials in 422 response
    assert not _response_contains_secret(resp.text)


# ── Test 4: Missing credentials produce safe 503 ─────────────────────────────
def test_design_missing_credentials(client):
    """When credentials are absent the endpoint returns a safe 503, no token."""
    with patch("app.api.design.credentials_configured", return_value=False):
        resp = client.post("/api/design", json={"prompt": "A pastel pink half-saree"})
    assert resp.status_code == 503
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] in ("NOT_CONFIGURED", "CONFIGURATION_ERROR")
    # Safe message — no raw CF errors, no credentials
    assert not _response_contains_secret(resp.text)


# ── Test 5: Cloudflare API error is handled safely ────────────────────────────
def test_design_cloudflare_error_is_sanitised(client):
    """Cloudflare 500 must not leak raw error text or credentials to client."""
    mock_cf_response = MagicMock()
    mock_cf_response.status_code = 500
    # Simulate a Cloudflare response that contains sensitive-looking text
    mock_cf_response.content = b'{"errors": [{"message": "internal error with token test_secret_token_never_in_response"}]}'
    mock_cf_response.headers = {"content-type": "application/json"}
    mock_cf_response.json.return_value = {"errors": [{"message": "internal"}]}

    with patch(
        "app.services.cloudflare_ai.httpx.AsyncClient",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(
            post=AsyncMock(return_value=mock_cf_response)
        )), __aexit__=AsyncMock(return_value=False))
    ):
        resp = client.post("/api/design", json={"prompt": "A luxury silk kurta in deep maroon"})

    assert resp.status_code == 500
    body = resp.json()
    assert body["success"] is False
    assert "error" in body
    # The raw Cloudflare error and any credential must NOT appear
    assert not _response_contains_secret(resp.text)
    assert "internal error" not in resp.text


# ── Test 6: Successful generation returns image ───────────────────────────────
@pytest.mark.asyncio
async def test_design_success():
    """
    Happy path — test the service layer directly to avoid slowapi rate-limit
    accumulation across the test session (the /api/design route has a 2/min cap).
    """
    from app.services.cloudflare_ai import generate_fashion_image

    mock_cf_response = MagicMock()
    mock_cf_response.status_code = 200
    mock_cf_response.content = b"fake-png-bytes"
    mock_cf_response.headers = {"content-type": "image/png"}

    with patch(
        "app.services.cloudflare_ai.httpx.AsyncClient",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(
            post=AsyncMock(return_value=mock_cf_response)
        )), __aexit__=AsyncMock(return_value=False))
    ):
        result = await generate_fashion_image(
            "Contemporary cotton kurta with geometric patterns under Rs 3000"
        )

    assert result.success is True
    assert result.image_base64 is not None
    assert result.image_base64.startswith("data:image/png;base64,")
    # Credentials must never appear in the result object
    assert TEST_TOKEN    not in (result.image_base64 or "")
    assert TEST_ACCOUNT  not in (result.image_base64 or "")


# ── Test 7: Credentials never appear in any response ─────────────────────────
def test_credentials_never_in_any_response(client):
    """Exhaustive check — run multiple scenarios and assert token never leaks."""
    scenarios = [
        ("GET",  "/",              None),
        ("GET",  "/api/health",    None),
        ("POST", "/api/design",    {"prompt": "x"}),  # too short → 422
    ]
    for method, path, body in scenarios:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json=body)
        assert not _response_contains_secret(resp.text), (
            f"Credential found in {method} {path} response!"
        )
