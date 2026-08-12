"""
api/products.py
===============
Vercel Python Serverless Function — GET /api/products/search

Query parameters:
    query    : str   (required, min 2 chars)
    category : str   (optional)
    color    : str   (optional)
    budget   : float (optional, max price in INR)
    limit    : int   (optional, 1-10, default 5)

Returns JSON:
    { "success": true,  "products": [...], "query": "...", "source": "H&M via RapidAPI" }
    { "success": false, "error": { "code": "...", "message": "..." } }

Security:
    RAPIDAPI_KEY lives in Vercel env vars only — never sent to or accepted from the client.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_HOST   = "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com"
_API_TIMEOUT    = 15          # seconds
_CACHE_TTL      = 300         # seconds
_cache: Dict[str, Any] = {}   # simple in-process cache

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _parse_price(raw: str) -> Optional[float]:
    digits = re.sub(r"[^\d.]", "", str(raw).replace(",", "").replace("\xa0", "").replace(" ", ""))
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def _is_space_sleeping(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "503" in msg or "unavailable" in msg or "loading" in msg


def _extract_products(raw: Any) -> List[Dict]:
    if not isinstance(raw, dict):
        return []
    results = raw.get("results", [])
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            items = first.get("products", [])
            if isinstance(items, list):
                return items
    if isinstance(raw.get("products"), list):
        return raw["products"]
    return []


def _normalise(item: Dict) -> Optional[Dict]:
    if not isinstance(item, dict):
        return None
    name = (item.get("name") or item.get("title") or "").strip()
    if not name:
        return None

    raw_url = item.get("url") or item.get("linkPdp") or ""
    if not raw_url:
        return None
    url = raw_url if raw_url.startswith("http") else f"https://www2.hm.com{raw_url}"

    price = _parse_price(str(
        item.get("price") or
        ((item.get("prices") or [{}])[0].get("value") or "") or ""
    ))

    image = None
    imgs = item.get("images") or item.get("image") or []
    if isinstance(imgs, list) and imgs:
        raw_img = imgs[0].get("url") or imgs[0].get("src") if isinstance(imgs[0], dict) else imgs[0]
        if raw_img:
            image = raw_img if str(raw_img).startswith("http") else f"https:{raw_img}"
    elif isinstance(imgs, str) and imgs:
        image = imgs if imgs.startswith("http") else f"https:{imgs}"

    brand    = (item.get("brand") or item.get("brandName") or "H&M").strip() or "H&M"
    category = (item.get("categoryName") or item.get("mainCategory") or "").strip() or None

    return {
        "name":     name,
        "brand":    brand,
        "price":    price,
        "currency": "INR",
        "image":    image,
        "url":      url,
        "category": category,
        "rating":   None,   # H&M API doesn't reliably expose ratings
        "source":   "H&M",
        "recommendation_score": None,  # set below
    }


def _score(product: Dict, category: Optional[str],
           color: Optional[str], budget: Optional[float]) -> int:
    score = 0
    prod_cat  = (product.get("category") or "").lower()
    prod_name = (product.get("name") or "").lower()
    price     = product.get("price")

    if category:
        cat_l = category.lower()
        if cat_l in prod_cat or prod_cat in cat_l:
            score += 40
        else:
            score += 10
    else:
        score += 20

    if color:
        score += 25 if color.lower() in prod_name else 5
    else:
        score += 12

    if budget is not None and price is not None:
        if price <= budget:
            score += 20
        elif price <= budget * 1.20:
            score += 10
    else:
        score += 10

    score += 15   # style/brand base
    return min(score, 100)


def _search_products(query: str, category: Optional[str],
                     color: Optional[str], budget: Optional[float],
                     limit: int) -> List[Dict]:
    import time as _time

    cache_key = f"{query}|{category}|{color}|{budget}|{limit}"
    if cache_key in _cache:
        ts, cached = _cache[cache_key]
        if _time.monotonic() - ts < _CACHE_TTL:
            return cached

    api_key  = os.getenv("RAPIDAPI_KEY",  "").strip()
    api_host = os.getenv("RAPIDAPI_HOST", _DEFAULT_HOST).strip()
    if not api_key:
        return []

    params: Dict[str, str] = {
        "country":     "in",
        "lang":        "en",
        "currentpage": "0",
        "pagesize":    str(min(limit * 3, 30)),
        "categories":  "ladies_all",
        "concepts":    "H&M",
        "sortBy":      "RELEVANCE",
        "keyword":     query,
    }
    if category:
        cat_l = category.lower()
        if any(k in cat_l for k in ("shirt", "top", "tshirt", "kurta", "blouse")):
            params["categories"] = "ladies_tops_all"
        elif any(k in cat_l for k in ("dress", "gown", "saree")):
            params["categories"] = "ladies_dresses_all"
        elif any(k in cat_l for k in ("jacket", "coat", "blazer")):
            params["categories"] = "ladies_jackets_coats"
        elif any(k in cat_l for k in ("jeans", "trouser", "pant", "skirt")):
            params["categories"] = "ladies_trousers_jeans"
        elif any(k in cat_l for k in ("men", "mens")):
            params["categories"] = "men_all"

    api_host_env = os.getenv("RAPIDAPI_HOST", _DEFAULT_HOST).strip()
    url = f"https://{api_host_env}/products/list?" + urllib.parse.urlencode(params)
    headers = {
        "x-rapidapi-key":  api_key,
        "x-rapidapi-host": api_host_env,
    }

    try:
        req  = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as resp:
            raw = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        logger.error("RapidAPI HTTP %d", exc.code)
        return []
    except Exception as exc:
        logger.error("RapidAPI request error: %s", type(exc).__name__)
        return []

    items = _extract_products(raw)
    normalised = []
    for item in items:
        p = _normalise(item)
        if p:
            p["recommendation_score"] = _score(p, category, color, budget)
            normalised.append(p)

    normalised.sort(key=lambda x: x.get("recommendation_score") or 0, reverse=True)
    results = normalised[:limit]

    _cache[cache_key] = (_time.monotonic(), results)
    return results


# ---------------------------------------------------------------------------
# Vercel handler
# ---------------------------------------------------------------------------

class handler(BaseHTTPRequestHandler):

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        qs     = urllib.parse.parse_qs(parsed.query)

        def _get(key: str, default: Optional[str] = None) -> Optional[str]:
            vals = qs.get(key, [])
            return vals[0].strip() if vals else default

        query = _get("query", "")
        if not query or len(query) < 2:
            self._send_json(422, _json_error(
                "INVALID_QUERY",
                "The 'query' parameter is required and must be at least 2 characters.",
            ))
            return

        if not os.getenv("RAPIDAPI_KEY", "").strip():
            self._send_json(503, _json_error(
                "NOT_CONFIGURED",
                "Product recommendations are temporarily unavailable.",
            ))
            return

        category = _get("category")
        color    = _get("color")
        budget_s = _get("budget")
        limit_s  = _get("limit", "5")

        budget: Optional[float] = None
        if budget_s:
            try:
                budget = float(budget_s)
            except ValueError:
                pass

        limit = 5
        try:
            limit = max(1, min(10, int(limit_s or "5")))
        except ValueError:
            pass

        logger.info("GET /api/products/search query=%r cat=%r color=%r budget=%s lim=%d",
                    query[:60], category, color, budget, limit)

        products = _search_products(query, category, color, budget, limit)

        self._send_json(200, {
            "success":  True,
            "products": products,
            "query":    query,
            "source":   "H&M via RapidAPI",
        })
