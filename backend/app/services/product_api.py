"""
backend/app/services/product_api.py
=====================================
Calls the RapidAPI H&M product search endpoint and normalises results.

API used : H&M Store Products API on RapidAPI
Host     : apidojo-hm-hennes-mauritz-v1.p.rapidapi.com
Endpoint : GET /products/list

Environment variables (never exposed to frontend):
    RAPIDAPI_KEY  — your RapidAPI key
    RAPIDAPI_HOST — defaults to apidojo-hm-hennes-mauritz-v1.p.rapidapi.com

Security rules:
    - Credentials read from env only; never logged.
    - Raw API errors never forwarded to caller.
    - Response fields always normalised; missing fields → None.

Scoring rubric (weighted match, 0-100):
    Category match : 40 pts
    Color match    : 25 pts
    Budget fit     : 20 pts
    Style / fabric : 15 pts
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.schemas.product import Product

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_HOST = "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com"
_API_TIMEOUT  = httpx.Timeout(15.0, connect=5.0)

# Simple in-process TTL cache: (query_key) → (timestamp, results)
# Avoids hammering RapidAPI for the exact same query within 5 min.
_CACHE_TTL_SECONDS = 300
_cache: Dict[str, Tuple[float, List[Product]]] = {}

# INR conversion rate (USD → INR) for price normalisation.
# H&M API returns prices in local currency; we keep them as-is but label INR.
_USD_TO_INR = 83.0


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def rapidapi_configured() -> bool:
    """Return True when a RAPIDAPI_KEY is present in the environment."""
    return bool(os.getenv("RAPIDAPI_KEY", "").strip())


async def search_products(
    query:    str,
    category: Optional[str] = None,
    color:    Optional[str] = None,
    budget:   Optional[float] = None,
    limit:    int = 5,
) -> List[Product]:
    """
    Search H&M products via RapidAPI and return normalised, ranked results.

    Args:
        query    : Free-text query built from the Gemini fashion spec.
        category : Optional category filter (shirt, dress, jacket, …).
        color    : Optional color hint (used for scoring only).
        budget   : Optional maximum price in INR.
        limit    : Maximum number of products to return (1-10).

    Returns:
        List of Product objects, sorted by recommendation_score descending.
        Returns an empty list when the API is unavailable or returns no results.
    """
    import time as _time

    # ── Cache lookup ─────────────────────────────────────────────────────────
    cache_key = f"{query}|{category}|{color}|{budget}|{limit}"
    if cache_key in _cache:
        ts, cached = _cache[cache_key]
        if _time.monotonic() - ts < _CACHE_TTL_SECONDS:
            logger.info("Product cache hit for key=%r", cache_key[:60])
            return cached

    # ── Credentials ──────────────────────────────────────────────────────────
    api_key  = os.getenv("RAPIDAPI_KEY",  "").strip()
    api_host = os.getenv("RAPIDAPI_HOST", _DEFAULT_HOST).strip()

    if not api_key:
        logger.warning("RAPIDAPI_KEY not set — product search disabled.")
        return []

    # ── Build request ────────────────────────────────────────────────────────
    url = f"https://{api_host}/products/list"
    params: Dict[str, Any] = {
        "country":    "in",       # India storefront
        "lang":       "en",
        "currentpage": "0",
        "pagesize":   str(min(limit * 3, 30)),   # fetch more, then rank
        "categories": "ladies_all",              # default; overridden below
        "concepts":   "H&M",
        "sortBy":     "RELEVANCE",
        "keyword":    query,
    }

    # Map category to H&M category codes
    if category:
        cat_lower = category.lower()
        if any(k in cat_lower for k in ("shirt", "top", "tshirt", "kurta", "blouse")):
            params["categories"] = "ladies_tops_all"
        elif any(k in cat_lower for k in ("dress", "gown", "saree")):
            params["categories"] = "ladies_dresses_all"
        elif any(k in cat_lower for k in ("jacket", "coat", "blazer", "outerwear")):
            params["categories"] = "ladies_jackets_coats"
        elif any(k in cat_lower for k in ("jeans", "trouser", "pant", "skirt")):
            params["categories"] = "ladies_trousers_jeans"
        elif any(k in cat_lower for k in ("men", "mens")):
            params["categories"] = "men_all"

    headers = {
        "x-rapidapi-key":  api_key,    # never logged
        "x-rapidapi-host": api_host,
    }

    # ── HTTP call ────────────────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=_API_TIMEOUT) as client:
            resp = await client.get(url, params=params, headers=headers)
    except httpx.TimeoutException:
        logger.error("RapidAPI H&M request timed out for query=%r", query[:60])
        return []
    except httpx.RequestError as exc:
        logger.error("RapidAPI network error: %s", type(exc).__name__)
        return []

    if resp.status_code == 401:
        logger.error("RapidAPI returned 401 — check RAPIDAPI_KEY.")
        return []
    if resp.status_code == 403:
        logger.error("RapidAPI returned 403 — subscription or permissions issue.")
        return []
    if resp.status_code == 429:
        logger.warning("RapidAPI rate limit hit.")
        return []
    if resp.status_code != 200:
        logger.error("RapidAPI returned unexpected status %d", resp.status_code)
        return []

    # ── Parse & normalise ────────────────────────────────────────────────────
    try:
        raw = resp.json()
    except Exception:
        logger.error("Could not parse RapidAPI response as JSON.")
        return []

    raw_products = _extract_product_list(raw)
    if not raw_products:
        logger.info("RapidAPI returned 0 products for query=%r", query[:60])
        return []

    normalised: List[Product] = []
    for item in raw_products:
        p = _normalise(item)
        if p is not None:
            p.recommendation_score = _score(p, category, color, budget)
            normalised.append(p)

    # Sort by score desc, cap at limit
    normalised.sort(key=lambda x: x.recommendation_score or 0, reverse=True)
    results = normalised[:limit]

    # ── Cache & return ────────────────────────────────────────────────────────
    import time as _time2
    _cache[cache_key] = (_time2.monotonic(), results)
    logger.info("RapidAPI returned %d products (after ranking) for query=%r",
                len(results), query[:60])
    return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_product_list(raw: Any) -> List[Dict]:
    """
    The H&M API returns:
      { "results": [ { "products": [...] } ] }
    Handle gracefully if the shape differs.
    """
    if not isinstance(raw, dict):
        return []

    # Primary path: raw["results"][0]["products"]
    results = raw.get("results", [])
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            items = first.get("products", [])
            if isinstance(items, list):
                return items

    # Fallback: flat list at top level
    if isinstance(raw.get("products"), list):
        return raw["products"]

    return []


def _normalise(item: Dict) -> Optional[Product]:
    """
    Map a raw H&M API product dict to our internal Product schema.
    Returns None if the item is clearly unusable (no name, no URL).
    """
    if not isinstance(item, dict):
        return None

    name = (item.get("name") or item.get("title") or "").strip()
    if not name:
        return None

    # URL
    url: Optional[str] = None
    raw_url = item.get("url") or item.get("linkPdp") or ""
    if raw_url:
        url = raw_url if raw_url.startswith("http") else f"https://www2.hm.com{raw_url}"

    if not url:
        return None

    # Price — H&M API gives price as a string like "₹1 999.00" or "1999.00"
    price: Optional[float] = None
    price_raw = (
        item.get("price")
        or (item.get("prices") or [{}])[0].get("value")
        or None
    )
    if price_raw is not None:
        price = _parse_price(str(price_raw))

    # Image
    image: Optional[str] = None
    images = item.get("images") or item.get("image") or []
    if isinstance(images, list) and images:
        img = images[0]
        raw_img = img.get("url") or img.get("src") or (img if isinstance(img, str) else None)
        if raw_img:
            image = raw_img if raw_img.startswith("http") else f"https:{raw_img}"
    elif isinstance(images, str) and images:
        image = images if images.startswith("http") else f"https:{images}"

    # Brand / category
    brand    = (item.get("brand") or item.get("brandName") or "H&M").strip() or "H&M"
    category = (item.get("categoryName") or item.get("mainCategory") or "").strip() or None

    # Rating — H&M API does not reliably provide ratings; leave as None
    rating: Optional[float] = None
    raw_rating = item.get("averageRating") or item.get("rating")
    if raw_rating is not None:
        try:
            rating = float(raw_rating)
        except (TypeError, ValueError):
            rating = None

    return Product(
        name=name,
        brand=brand,
        price=price,
        currency="INR",
        image=image,
        url=url,
        category=category,
        rating=rating,
        source="H&M",
    )


def _parse_price(raw: str) -> Optional[float]:
    """Extract a numeric price from strings like '₹1 999.00', '1,999', '19.99'."""
    import re
    digits = re.sub(r"[^\d.]", "", raw.replace(",", "").replace("\xa0", "").replace(" ", ""))
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def _score(
    product:  Product,
    category: Optional[str],
    color:    Optional[str],
    budget:   Optional[float],
) -> int:
    """
    Return a 0-100 weighted recommendation score.

    Weights:
        Category match : 40 pts
        Color match    : 25 pts
        Budget fit     : 20 pts
        Style / brand  : 15 pts   (always awarded; H&M is a style-relevant brand)
    """
    score = 0

    # ── Category (40 pts) ────────────────────────────────────────────────────
    if category and product.category:
        if category.lower() in product.category.lower() or \
           product.category.lower() in category.lower():
            score += 40
        else:
            score += 10   # partial credit — at least it's a fashion item
    else:
        score += 20       # unknown category — give neutral credit

    # ── Color (25 pts) ───────────────────────────────────────────────────────
    if color:
        # Check if the color hint appears in name or category
        name_lower = product.name.lower()
        color_lower = color.lower()
        if color_lower in name_lower:
            score += 25
        else:
            score += 5    # color unknown / not mentioned
    else:
        score += 12       # no color constraint — neutral

    # ── Budget (20 pts) ──────────────────────────────────────────────────────
    if budget is not None and product.price is not None:
        if product.price <= budget:
            score += 20
        elif product.price <= budget * 1.20:
            score += 10   # within 20% over budget — partial credit
        # else 0 — over budget
    else:
        score += 10       # no price constraint — neutral

    # ── Style / brand (15 pts) — H&M always gets base style score ───────────
    score += 15

    return min(score, 100)
