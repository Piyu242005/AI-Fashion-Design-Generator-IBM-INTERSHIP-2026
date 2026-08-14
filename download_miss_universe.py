"""
Miss Universe Image Downloader v4
Sources tried in order:
  1. Wikimedia Commons API  (real contestant photos, free licence, no key needed)
  2. Pexels API             (free key at pexels.com/api)
  3. Unsplash API           (free key at unsplash.com/developers)

Run:
  python download_miss_universe.pY

Optional API keys (PowerShell):
  $env:PEXELS_API_KEY   = "your_key"
  $env:UNSPLASH_ACCESS_KEY = "your_key"
"""

import os
import sys
import time
import zipfile
import requests

# ── Config ────────────────────────────────────────────────────────────
OUT    = "Miss_Universe_1000"
ZIP    = "Miss_Universe_1000.zip"
TARGET = 1000

HEADERS = {
    "User-Agent": "MissUniverseDatasetDownloader/4.0 (educational; python-requests)"
}

os.makedirs(OUT, exist_ok=True)
downloaded = 0   # global counter


# =====================================================================
# HELPERS
# =====================================================================

def log(msg):
    """Print safely on any platform/encoding."""
    try:
        print(msg)
        sys.stdout.flush()
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))
        sys.stdout.flush()


def save_image(content, ext=".jpg"):
    """Save bytes as next numbered file. Returns True on success."""
    global downloaded
    if len(content) < 5000:
        return False
    path = os.path.join(OUT, f"{downloaded + 1:04d}{ext}")
    with open(path, "wb") as f:
        f.write(content)
    downloaded += 1
    return True


def ext_from_url(url):
    low = url.split("?")[0].lower()
    for e in (".png", ".webp", ".jpeg", ".gif"):
        if low.endswith(e):
            return e
    return ".jpg"


def http_get(url, params=None, extra_headers=None, retries=5, backoff=4):
    """Resilient HTTP GET — retries on 429/errors with exponential back-off."""
    hdrs = {**HEADERS, **(extra_headers or {})}
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=hdrs, timeout=30)
            if r.status_code == 200:
                return r
            if r.status_code == 429:
                wait = backoff * attempt * 2
                log(f"    [429 rate-limit] waiting {wait}s (attempt {attempt})")
                time.sleep(wait)
                continue
            log(f"    [warn] HTTP {r.status_code} on attempt {attempt}")
        except Exception as e:
            log(f"    [warn] attempt {attempt}: {e}")
        time.sleep(backoff * attempt)
    return None


# =====================================================================
# SOURCE 1 -- WIKIMEDIA COMMONS  (no API key needed)
# =====================================================================

WM_API = "https://commons.wikimedia.org/w/api.php"


def wm_call(params, retries=6, backoff=6):
    """Call Wikimedia API JSON endpoint with rate-limit handling."""
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


def wm_category_members(category):
    """Return all members (files + subcategories) of a Wikimedia category."""
    members, cont = [], {}
    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": category,
            "cmtype": "file|subcat",
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
        time.sleep(1)
    return members


def wm_image_url(title):
    """Resolve a Wikimedia File: title to a direct download URL."""
    data = wm_call({
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1200,
    })
    if not data:
        return None
    for page in data["query"]["pages"].values():
        if "imageinfo" in page:
            info = page["imageinfo"][0]
            return info.get("thumburl") or info.get("url")
    return None


def source_wikimedia():
    global downloaded
    log("\n=== SOURCE 1: Wikimedia Commons ===")

    # Collect subcategories from the root contestant category
    root_members = wm_category_members("Category:Miss Universe contestants")
    subcats = [
        x["title"] for x in root_members
        if x["ns"] == 14 and "Miss Universe" in x["title"]
    ]
    log(f"  Found {len(subcats)} subcategories")

    # Gather file titles from every subcategory
    file_titles = []
    for cat in subcats:
        if downloaded + len(file_titles) >= TARGET * 2:
            break
        log(f"  Scanning: {cat}")
        time.sleep(2)                  # polite pause between category scans
        for item in wm_category_members(cat):
            if item["ns"] == 6:        # namespace 6 = File:
                file_titles.append(item["title"])

    file_titles = list(dict.fromkeys(file_titles))   # deduplicate
    log(f"  Collected {len(file_titles)} unique file titles")

    # Download each image
    for title in file_titles:
        if downloaded >= TARGET:
            break
        try:
            url = wm_image_url(title)
            if not url:
                continue
            r = http_get(url)
            if r and save_image(r.content, ext_from_url(url)):
                log(f"  [WM {downloaded}/{TARGET}] {title[:70]}")
            time.sleep(0.4)
        except Exception as e:
            log(f"  Skipped ({e})")

    log(f"  Wikimedia done. Total so far: {downloaded}")


# =====================================================================
# SOURCE 2 -- PEXELS  (free key from pexels.com/api)
# =====================================================================

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")


def source_pexels():
    global downloaded
    if downloaded >= TARGET:
        return

    log("\n=== SOURCE 2: Pexels ===")

    if not PEXELS_KEY:
        log("  PEXELS_API_KEY not set -- skipping.")
        log("  1. Go to https://www.pexels.com/api/ and get a free key")
        log("  2. In PowerShell: $env:PEXELS_API_KEY='YOUR_KEY'")
        log("  3. Re-run this script")
        return

    queries = [
        "miss universe",
        "miss universe pageant",
        "beauty queen crown",
        "pageant evening gown",
    ]
    for q_idx, query in enumerate(queries):
        page = 1
        while downloaded < TARGET:
            r = http_get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": 80, "page": page},
                extra_headers={"Authorization": PEXELS_KEY},
            )
            if not r:
                break
            photos = r.json().get("photos", [])
            if not photos:
                break
            for photo in photos:
                if downloaded >= TARGET:
                    break
                img_url = photo["src"].get("large2x") or photo["src"]["original"]
                img_r = http_get(img_url)
                if img_r and save_image(img_r.content, ".jpg"):
                    log(f"  [Pexels {downloaded}/{TARGET}] id={photo['id']}")
                time.sleep(0.2)
            page += 1
            time.sleep(0.5)

    log(f"  Pexels done. Total so far: {downloaded}")


# =====================================================================
# SOURCE 3 -- UNSPLASH  (free key from unsplash.com/developers)
# =====================================================================

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")


def source_unsplash():
    global downloaded
    if downloaded >= TARGET:
        return

    log("\n=== SOURCE 3: Unsplash ===")

    if not UNSPLASH_KEY:
        log("  UNSPLASH_ACCESS_KEY not set -- skipping.")
        log("  1. Go to https://unsplash.com/developers and get a free key")
        log("  2. In PowerShell: $env:UNSPLASH_ACCESS_KEY='YOUR_KEY'")
        log("  3. Re-run this script")
        return

    queries = [
        "miss universe",
        "beauty pageant",
        "pageant crown",
        "miss universe winner",
    ]
    for query in queries:
        page = 1
        while downloaded < TARGET:
            r = http_get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 30, "page": page},
                extra_headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            )
            if not r:
                break
            results = r.json().get("results", [])
            if not results:
                break
            for photo in results:
                if downloaded >= TARGET:
                    break
                img_url = photo["urls"].get("full") or photo["urls"]["regular"]
                img_r = http_get(img_url)
                if img_r and save_image(img_r.content, ".jpg"):
                    log(f"  [Unsplash {downloaded}/{TARGET}] id={photo['id']}")
                time.sleep(0.2)
            page += 1
            time.sleep(1)   # Unsplash free tier: 50 req/hr

    log(f"  Unsplash done. Total so far: {downloaded}")


# =====================================================================
# MAIN
# =====================================================================

log(f"Target : {TARGET} images")
log(f"Output : {OUT}/")
log(f"Sources: Wikimedia Commons -> Pexels -> Unsplash")
log("")

source_wikimedia()

if downloaded < TARGET:
    source_pexels()

if downloaded < TARGET:
    source_unsplash()

if downloaded < TARGET:
    log(f"\n[info] Only {downloaded} images collected.")
    log("       Add PEXELS_API_KEY and/or UNSPLASH_ACCESS_KEY to get more.")

log(f"\nTotal downloaded: {downloaded} images")

# ── Build ZIP ─────────────────────────────────────────────────────────
if downloaded > 0:
    log("Building ZIP...")
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(OUT)):
            fp = os.path.join(OUT, fn)
            if os.path.isfile(fp):
                z.write(fp, arcname=fn)
    log(f"Done!  ZIP saved -> {ZIP}  ({downloaded} images)")
else:
    log("No images downloaded -- ZIP not created.")
