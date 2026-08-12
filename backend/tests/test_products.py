"""
backend/tests/test_products.py
================================
Unit tests for the GET /api/products/search endpoint and the product_api service.

All RapidAPI HTTP calls are fully mocked — no real network requests are made.

Tests:
  1. Successful product search returns normalised products
  2. Empty results are handled gracefully
  3. Invalid / malformed API response is handled gracefully
  4. API timeout returns empty list (does not raise)
  5. Missing RAPIDAPI_KEY returns 503 with safe message
  6. Rate-limited response (429) returns empty list
  7. Product normalisation — all required fields are set correctly
  8. Query too short — 422 validation error
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── Env must be set BEFORE app is imported ───────────────────────────────────
os.environ.setdefault("CLOUDFLARE_ACCOUNT_ID", "test_account_id")
os.environ.setdefault("CLOUDFLARE_API_TOKEN",  "test_cf_token")
os.environ["RAPIDAPI_KEY"]  = "test_rapidapi_key_never_in_response"
os.environ["RAPIDAPI_HOST"] = "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com"

from app.main import app                         # noqa: E402
from app.services.product_api import (          # noqa: E402
    _normalise, _score, _parse_price, _extract_product_list,
)
from app.schemas.product import Product         # noqa: E402

REAL_KEY = "test_rapidapi_key_never_in_response"


@pytest.fixture
def client():
    """Fresh TestClient per test — avoids rate-limiter accumulation."""
    with TestClient(app) as c:
        yield c


# ── Shared fixtures ───────────────────────────────────────────────────────────

SAMPLE_RAW_ITEM = {
    "name":         "H&M Black Cotton Shirt",
    "url":          "/en_in/productpage.0123456.html",
    "images":       [{"url": "//lp2.hm.com/hmgoepprod?set=key[img_url],value[/0123456.jpg]"}],
    "price":        "1999.00",
    "brand":        "H&M",
    "categoryName": "Tops",
    "averageRating": None,
}

SAMPLE_API_RESPONSE = {
    "results": [{"products": [SAMPLE_RAW_ITEM]}]
}


def _make_mock_response(status: int, json_data=None):
    mock = MagicMock()
    mock.status_code = status
    if json_data is not None:
        mock.json.return_value = json_data
    return mock


def _patch_httpx(response_mock):
    async_client = AsyncMock()
    async_client.__aenter__ = AsyncMock(return_value=async_client)
    async_client.__aexit__ = AsyncMock(return_value=False)
    async_client.get = AsyncMock(return_value=response_mock)
    return patch("app.services.product_api.httpx.AsyncClient", return_value=async_client)


# ── Test 1: Successful product search ─────────────────────────────────────────
def test_products_search_success(client):
    """Happy path — API returns products, endpoint returns normalised cards."""
    mock_resp = _make_mock_response(200, SAMPLE_API_RESPONSE)

    with _patch_httpx(mock_resp), \
         patch("app.api.products.rapidapi_configured", return_value=True), \
         patch("app.services.product_api.rapidapi_configured", return_value=True):
        import app.services.product_api as _svc
        _svc._cache.clear()
        resp = client.get("/api/products/search?query=black+cotton+shirt&limit=5")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["products"], list)
    assert len(data["products"]) == 1

    p = data["products"][0]
    assert p["name"]   == "H&M Black Cotton Shirt"
    assert p["brand"]  == "H&M"
    assert p["price"]  == 1999.0
    assert p["source"] == "H&M"
    assert p["url"].startswith("https://")
    assert p["recommendation_score"] is not None

    # RAPIDAPI_KEY must never appear in the response
    assert REAL_KEY not in resp.text


# ── Test 2: Empty results ─────────────────────────────────────────────────────
def test_products_search_empty_results(client):
    """API returns an empty product list — endpoint returns [] gracefully."""
    mock_resp = _make_mock_response(200, {"results": [{"products": []}]})

    with _patch_httpx(mock_resp), \
         patch("app.api.products.rapidapi_configured", return_value=True):
        import app.services.product_api as _svc
        _svc._cache.clear()
        resp = client.get("/api/products/search?query=unknown+style+zxq99")

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["products"] == []


# ── Test 3: Malformed API response ────────────────────────────────────────────
def test_products_search_malformed_response(client):
    """API returns garbage JSON structure — must return empty list, not crash."""
    mock_resp = _make_mock_response(200, {"unexpected_key": "garbage"})

    with _patch_httpx(mock_resp), \
         patch("app.api.products.rapidapi_configured", return_value=True):
        import app.services.product_api as _svc
        _svc._cache.clear()
        resp = client.get("/api/products/search?query=blazer")

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["products"] == []


# ── Test 4: API timeout ───────────────────────────────────────────────────────
def test_products_search_timeout(client):
    """Timeout from RapidAPI — must return empty list, not 500."""
    import httpx

    async_client = AsyncMock()
    async_client.__aenter__ = AsyncMock(return_value=async_client)
    async_client.__aexit__ = AsyncMock(return_value=False)
    async_client.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))

    with patch("app.services.product_api.httpx.AsyncClient", return_value=async_client), \
         patch("app.api.products.rapidapi_configured", return_value=True):
        import app.services.product_api as _svc
        _svc._cache.clear()
        resp = client.get("/api/products/search?query=dress")

    assert resp.status_code == 200
    data = resp.json()
    assert data["products"] == []


# ── Test 5: Missing RAPIDAPI_KEY returns 503 ─────────────────────────────────
def test_products_search_missing_credentials(client):
    """When RAPIDAPI_KEY is absent the endpoint returns a safe 503."""
    with patch("app.api.products.rapidapi_configured", return_value=False):
        resp = client.get("/api/products/search?query=kurta")

    assert resp.status_code == 503
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_CONFIGURED"
    # The real key value must never appear in any response
    assert REAL_KEY not in resp.text


# ── Test 6: Rate-limit (429) returns empty list ───────────────────────────────
def test_products_search_rate_limited(client):
    """429 from RapidAPI — must return empty list, not 429 to client."""
    mock_resp = _make_mock_response(429)

    with _patch_httpx(mock_resp), \
         patch("app.api.products.rapidapi_configured", return_value=True):
        import app.services.product_api as _svc
        _svc._cache.clear()
        resp = client.get("/api/products/search?query=jeans")

    assert resp.status_code == 200
    data = resp.json()
    assert data["products"] == []


# ── Test 7: Product normalisation ────────────────────────────────────────────
def test_product_normalisation():
    """Unit-test the _normalise() and helper functions directly (no HTTP)."""
    # Full item
    product = _normalise(SAMPLE_RAW_ITEM)
    assert product is not None
    assert product.name     == "H&M Black Cotton Shirt"
    assert product.brand    == "H&M"
    assert product.price    == 1999.0
    assert product.currency == "INR"
    assert product.source   == "H&M"
    assert product.url.startswith("https://www2.hm.com")
    assert product.image is not None
    assert product.rating is None   # H&M API doesn't reliably provide ratings

    # Item with no name — should be rejected
    assert _normalise({"price": "100"}) is None

    # Item with no URL — should be rejected
    assert _normalise({"name": "Test"}) is None

    # Price parsing
    assert _parse_price("₹1 999.00") == 1999.0
    assert _parse_price("1,999.99")  == 1999.99
    assert _parse_price("19.99")     == 19.99
    assert _parse_price("")          is None

    # _extract_product_list helper
    assert _extract_product_list(SAMPLE_API_RESPONSE) == [SAMPLE_RAW_ITEM]
    assert _extract_product_list({})                  == []
    assert _extract_product_list(None)                == []   # type: ignore[arg-type]

    # Scoring: category + color + budget + brand all match → high score
    p = Product(name="Black Cotton Shirt", brand="H&M", price=1500.0,
                currency="INR", url="https://x.com", source="H&M")
    score = _score(p, category="shirt", color="black", budget=2000.0)
    assert 0 <= score <= 100
    assert score >= 80   # should score high

    # Over-budget product scores lower on budget component
    p_expensive = Product(name="Premium Blazer", brand="H&M", price=5000.0,
                          currency="INR", url="https://x.com", source="H&M")
    score_over = _score(p_expensive, category="blazer", color="black", budget=2000.0)
    assert score_over < score


# ── Test 8: Query validation ──────────────────────────────────────────────────
def test_products_search_query_too_short(client):
    """Query shorter than 2 chars should be rejected with 422."""
    resp = client.get("/api/products/search?query=x")
    assert resp.status_code == 422
