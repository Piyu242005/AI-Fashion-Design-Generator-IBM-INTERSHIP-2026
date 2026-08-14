"""
 Miss Universe Image Downloader v5
===================================
Pipeline:
  Wikimedia Commons
       ↓
  All Miss Universe contestant categories (year + individual)
       ↓
  Resolve ORIGINAL / highest-resolution image URL
       ↓
  Remove duplicate URLs
       ↓
  Reject tiny images  (< 800 px wide OR < 1000 px tall)
       ↓
  Reject blurry images (Laplacian variance < BLUR_THRESHOLD)
       ↓
  Prefer portrait orientation
       ↓
  Score each image (resolution + portrait bonus)
       ↓
  Randomly select the BEST 10,000
       ↓
  Save as numbered files + build one ZIP

Requirements:
  pip install requests pillow numpy

Run:
  python download_miss_universe.py

Optional – speed up with more threads:
  set DOWNLOAD_THREADS=16   (default: 8)
"""

import io
import os
import sys
import time
import random
import zipfile
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# ── Try importing image-quality libs (optional but recommended) ─────────
try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[warn] Pillow/numpy not found — size/blur filters disabled.")
    print("       Run:  pip install pillow numpy")

# =====================================================================
# CONFIG
# =====================================================================

OUT     = "Miss_Universe_10000"
ZIP     = "Miss_Universe_10000.zip"
TARGET  = 10_000

# Quality filters (only applied when Pillow is available)
MIN_WIDTH      = 800    # pixels
MIN_HEIGHT     = 1000   # pixels
BLUR_THRESHOLD = 80.0   # Laplacian variance — lower = blurrier; 80 is a good cutoff

# Parallelism
THREADS = int(os.environ.get("DOWNLOAD_THREADS", "8"))

# Wikimedia Commons root categories to crawl
WM_ROOT_CATEGORIES = [
    "Category:Miss Universe contestants",
    "Category:Miss Universe",
]

HEADERS = {
    "User-Agent": "MissUniverseDatasetBuilder/5.0 (educational; python-requests)"
}

WM_API = "https://commons.wikimedia.org/w/api.php"

os.makedirs(OUT, exist_ok=True)

# Thread-safe counter
_lock       = threading.Lock()
_downloaded = 0
_skipped    = 0


# =====================================================================
# HELPERS
# =====================================================================

def log(msg):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)


def inc_downloaded():
    global _downloaded
    with _lock:
        _downloaded += 1
        return _downloaded


def inc_skipped():
    global _skipped
    with _lock:
        _skipped += 1


def next_filename(ext=".jpg"):
    """Return the next available numbered filepath (thread-safe)."""
    with _lock:
        n = _downloaded + 1
    return os.path.join(OUT, f"{n:05d}{ext}")


def ext_from_url(url):
    low = url.split("?")[0].lower()
    for e in (".png", ".webp", ".jpeg", ".gif"):
        if low.endswith(e):
            return e
    return ".jpg"


def http_get(url, params=None, extra_headers=None, retries=5, backoff=3):
    """Resilient HTTP GET with exponential back-off on 429/errors."""
    hdrs = {**HEADERS, **(extra_headers or {})}
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=hdrs, timeout=40)
            if r.status_code == 200:
                return r
            if r.status_code == 429:
                wait = backoff * attempt * 3
                log(f"    [429] waiting {wait}s")
                time.sleep(wait)
                continue
            log(f"    [warn] HTTP {r.status_code} attempt {attempt} — {url[:80]}")
        except Exception as e:
            log(f"    [warn] attempt {attempt}: {e}")
        time.sleep(backoff * attempt)
    return None


# =====================================================================
# WIKIMEDIA API HELPERS
# =====================================================================

def wm_call(params, retries=6, backoff=5):
    """Call the Wikimedia Commons JSON API with rate-limit handling."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(WM_API, params=params, headers=HEADERS, timeout=30)
            if r.status_code == 200 and r.text.strip():
                return r.json()
            if r.status_code == 429:
                wait = backoff * attempt * 3
                log(f"    [WM 429] waiting {wait}s (attempt {attempt})")
                time.sleep(wait)
                continue
            log(f"    [WM warn] HTTP {r.status_code} attempt {attempt}")
        except Exception as e:
            log(f"    [WM error] attempt {attempt}: {e}")
        time.sleep(backoff * attempt)
    return None


def wm_category_members(category, ns_filter="file|subcat"):
    """Return all members of a Wikimedia Commons category (paginated)."""
    members, cont = [], {}
    while True:
        params = {
            "action":  "query",
            "format":  "json",
            "list":    "categorymembers",
            "cmtitle": category,
            "cmtype":  ns_filter,
            "cmlimit": "500",
            **cont,
        }
        data = wm_call(params)
        if not data:
            break
        members.extend(data["query"]["categorymembers"])
        if "continue" not in data:
            break
        cont = data["continue"]
        time.sleep(0.5)
    return members


def wm_resolve_image_info_batch(titles):
    """
    Resolve a batch of File: titles to (url, width, height) via imageinfo.
    Returns a dict: title -> (url, width, height)
    Requests the ORIGINAL image (no thumb), so we get full resolution metadata.
    """
    result = {}
    # API allows up to 50 titles per request
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        data = wm_call({
            "action":  "query",
            "format":  "json",
            "titles":  "|".join(chunk),
            "prop":    "imageinfo",
            "iiprop":  "url|size",
        })
        if not data:
            continue
        for page in data["query"]["pages"].values():
            if "imageinfo" in page:
                info = page["imageinfo"][0]
                url  = info.get("url", "")
                w    = info.get("width", 0)
                h    = info.get("height", 0)
                t    = page.get("title", "")
                result[t] = (url, w, h)
        time.sleep(0.3)
    return result


# =====================================================================
# CATEGORY CRAWL
# =====================================================================

def crawl_all_file_titles():
    """
    Depth-first crawl of all Miss Universe contestant categories.
    Returns a list of (File: title, width, height, url) tuples — highest
    resolution files only, deduplicated by URL.
    """
    log("\n=== Crawling Wikimedia Commons categories ===")

    visited_cats  = set()
    file_titles   = []       # ordered, deduplicated File: titles
    seen_titles   = set()
    cats_queue    = list(WM_ROOT_CATEGORIES)

    while cats_queue:
        cat = cats_queue.pop(0)
        if cat in visited_cats:
            continue
        visited_cats.add(cat)
        log(f"  Scanning: {cat}")

        members = wm_category_members(cat, ns_filter="file|subcat")
        time.sleep(1)

        for item in members:
            ns    = item["ns"]
            title = item["title"]

            if ns == 14:  # subcategory — enqueue if relevant
                lower = title.lower()
                if any(k in lower for k in (
                    "miss universe", "contestant", "pageant",
                    "national costume", "evening gown", "swimsuit",
                    "swimwear", "preliminary", "official portrait",
                )):
                    if title not in visited_cats:
                        cats_queue.append(title)

            elif ns == 6:  # File:
                if title not in seen_titles:
                    seen_titles.add(title)
                    file_titles.append(title)

    log(f"  Total unique file titles collected: {len(file_titles)}")
    return file_titles


# =====================================================================
# IMAGE QUALITY FILTER
# =====================================================================

def score_image(content, width, height):
    """
    Returns (passes: bool, score: float).
    passes=False means the image should be rejected.
    score is used for ranking — higher is better.
    Requires Pillow + numpy.
    """
    if not HAS_PIL:
        # No filtering possible — accept everything
        return True, float(width * height)

    # ── Size guard ────────────────────────────────────────────────────
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False, 0.0

    # ── Decode image ─────────────────────────────────────────────────
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        return False, 0.0

    actual_w, actual_h = img.size

    # ── Minimum size re-check from actual pixels ──────────────────────
    if actual_w < MIN_WIDTH or actual_h < MIN_HEIGHT:
        return False, 0.0

    # ── Blurriness check (Laplacian variance) ─────────────────────────
    gray = np.array(img.convert("L"), dtype=np.float32)
    # Laplacian kernel
    lap = (
        gray[:-2, 1:-1] + gray[2:, 1:-1] +
        gray[1:-1, :-2] + gray[1:-1, 2:] -
        4 * gray[1:-1, 1:-1]
    )
    blur_score = float(np.var(lap))
    if blur_score < BLUR_THRESHOLD:
        return False, 0.0

    # ── Score: resolution × portrait bonus × sharpness factor ─────────
    portrait_bonus = 1.2 if actual_h > actual_w else 1.0
    score = actual_w * actual_h * portrait_bonus * min(blur_score / 500.0, 2.0)

    return True, score


# =====================================================================
# DOWNLOAD WORKER
# =====================================================================

def download_one(task):
    """
    task = (title, url, width, height)
    Returns (score, content, ext) or None if rejected/failed.
    """
    title, url, width, height = task

    # Pre-filter by metadata dimensions before downloading
    if HAS_PIL and (width < MIN_WIDTH or height < MIN_HEIGHT):
        inc_skipped()
        return None

    r = http_get(url)
    if not r or len(r.content) < 10_000:
        inc_skipped()
        return None

    passes, score = score_image(r.content, width, height)
    if not passes:
        inc_skipped()
        return None

    return (score, r.content, ext_from_url(url), title)


# =====================================================================
# MAIN PIPELINE
# =====================================================================

def main():
    global _downloaded

    log(f"Target  : {TARGET:,} images")
    log(f"Output  : {OUT}/")
    log(f"Threads : {THREADS}")
    log(f"Filters : min {MIN_WIDTH}×{MIN_HEIGHT}px | blur>{BLUR_THRESHOLD} | Pillow={'yes' if HAS_PIL else 'NO (install pillow numpy)'}")
    log("")

    # ── STEP 1: Crawl all category members ────────────────────────────
    file_titles = crawl_all_file_titles()

    if not file_titles:
        log("[error] No file titles found. Check network / Wikimedia API.")
        sys.exit(1)

    # ── STEP 2: Resolve image URLs + dimensions in batches ────────────
    log(f"\n=== Resolving image info for {len(file_titles):,} files ===")
    info_map = {}
    batch_size = 50
    for i in range(0, len(file_titles), batch_size):
        chunk = file_titles[i:i + batch_size]
        batch_result = wm_resolve_image_info_batch(chunk)
        info_map.update(batch_result)
        done = min(i + batch_size, len(file_titles))
        log(f"  Resolved {done:,}/{len(file_titles):,} ...")

    log(f"  Info resolved for {len(info_map):,} files.")

    # ── STEP 3: Build task list — deduplicate by URL ──────────────────
    seen_urls = set()
    tasks = []
    for title, (url, w, h) in info_map.items():
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        tasks.append((title, url, w, h))

    log(f"  Unique URLs after dedup: {len(tasks):,}")

    # Shuffle so we don't always grab the same subset if TARGET < total
    random.shuffle(tasks)

    # ── STEP 4: Parallel download + quality filter ────────────────────
    log(f"\n=== Downloading & filtering (up to {len(tasks):,} candidates) ===")

    scored_results = []   # list of (score, content, ext, title)

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(download_one, t): t for t in tasks}
        done_count = 0
        for future in as_completed(futures):
            done_count += 1
            result = future.result()
            if result is not None:
                scored_results.append(result)
                n = len(scored_results)
                if done_count % 100 == 0 or n % 500 == 0:
                    log(f"  Processed {done_count:,}/{len(tasks):,} | accepted {n:,} | skipped {_skipped:,}")

            # Stop fetching once we have enough candidates (3× target for ranking)
            if len(scored_results) >= TARGET * 3:
                log("  Reached 3× candidate buffer — stopping early.")
                executor.shutdown(wait=False, cancel_futures=True)
                break

    log(f"\n  Candidates accepted: {len(scored_results):,}")

    # ── STEP 5: Rank and select best TARGET images ────────────────────
    log(f"\n=== Ranking and selecting best {TARGET:,} images ===")
    scored_results.sort(key=lambda x: x[0], reverse=True)
    selected = scored_results[:TARGET]
    log(f"  Selected {len(selected):,} images.")

    # ── STEP 6: Save to disk ──────────────────────────────────────────
    log(f"\n=== Saving to {OUT}/ ===")
    for idx, (score, content, ext, title) in enumerate(selected, start=1):
        path = os.path.join(OUT, f"{idx:05d}{ext}")
        with open(path, "wb") as f:
            f.write(content)
        if idx % 500 == 0:
            log(f"  Saved {idx:,}/{len(selected):,} ...")

    _downloaded = len(selected)
    log(f"  Saved {_downloaded:,} images.")

    # ── STEP 7: Build ZIP ─────────────────────────────────────────────
    if _downloaded > 0:
        log(f"\n=== Building {ZIP} ===")
        with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for fn in sorted(os.listdir(OUT)):
                fp = os.path.join(OUT, fn)
                if os.path.isfile(fp):
                    z.write(fp, arcname=fn)
        size_mb = os.path.getsize(ZIP) / (1024 * 1024)
        log(f"  Done! ZIP saved -> {ZIP}  ({_downloaded:,} images, {size_mb:.1f} MB)")
    else:
        log("[warn] No images saved — ZIP not created.")

    log(f"\nTotal downloaded : {_downloaded:,}")
    log(f"Total skipped    : {_skipped:,}")


if __name__ == "__main__":
    main()
