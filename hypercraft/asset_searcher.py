"""
hypercraft/asset_searcher.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Automated Entity Visual Search & Reference Asset Generator.
Searches Wikipedia/Wikimedia and web sources for entities mentioned in dialogue,
downloads the image, and crafts a high-impact circular pop-up badge with a glowing outline.
"""

import os
import re
import urllib.request
import urllib.parse
import json
from PIL import Image, ImageDraw, ImageOps

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
ASSET_CACHE_DIR = os.path.join(ROOT_DIR, "clips", "asset_cache")
os.makedirs(ASSET_CACHE_DIR, exist_ok=True)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}


def _download_url_with_headers(url: str, output_path: str) -> bool:
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            if len(data) > 1000:
                with open(output_path, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"[!] Download error for {url}: {e}")
    return False


def search_entity_image(query: str) -> str | None:
    """
    Finds a pristine, relevant portrait or reference image for an entity.
    """
    clean_q = re.sub(r"[^a-zA-Z0-9\s]", "", query).strip()
    if not clean_q:
        return None

    # Check local cache
    cached_path = os.path.join(ASSET_CACHE_DIR, f"{clean_q.lower().replace(' ', '_')}.png")
    if os.path.exists(cached_path):
        return cached_path

    raw_download = os.path.join(ASSET_CACHE_DIR, f"raw_{clean_q.lower().replace(' ', '_')}.jpg")

    # 1. Wikimedia API with standard browser headers
    try:
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&format=json"
            f"&prop=pageimages&pithumbsize=600&generator=search"
            f"&gsrsearch={urllib.parse.quote(clean_q)}&gsrlimit=3"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for _, p in pages.items():
                if "thumbnail" in p:
                    img_url = p["thumbnail"]["source"]
                    if _download_url_with_headers(img_url, raw_download):
                        return create_circular_badge(raw_download, cached_path, clean_q)
    except Exception as e:
        print(f"[!] Wiki search failed for '{clean_q}': {e}")

    # 2. Bing Image Search Fallback
    try:
        bing_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(clean_q + ' portrait')}&FORM=HDRSC2"
        req = urllib.request.Request(bing_url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Extract murl from bing json attributes
            matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', html)
            for m in matches:
                if m.endswith((".jpg", ".png", ".jpeg")):
                    if _download_url_with_headers(m, raw_download):
                        return create_circular_badge(raw_download, cached_path, clean_q)
    except Exception as e:
        print(f"[!] Bing search fallback failed for '{clean_q}': {e}")

    return None


def create_circular_badge(src_image: str, output_path: str, label: str, diameter: int = 400) -> str:
    """
    Transforms a raw image into a floating circular reference badge
    matching the exact style in https://www.youtube.com/shorts/L9IGhWkwpgo:
      - 1080x1920 transparent canvas
      - Circular crop of the subject
      - High-contrast white border + outer accent ring
      - Positioned in bottom-center above captions (y: 1300)
    """
    with Image.open(src_image).convert("RGBA") as img:
        img_sq = ImageOps.fit(img, (diameter, diameter), centering=(0.5, 0.4))

        mask = Image.new("L", (diameter, diameter), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, diameter, diameter), fill=255)

        canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        x_pos = (1080 - diameter) // 2
        y_pos = 1300

        draw_canvas = ImageDraw.Draw(canvas)
        ring_r = diameter + 16
        ring_x = (1080 - ring_r) // 2
        ring_y = y_pos - 8

        # Draw outer glowing ring (Yellow/White)
        draw_canvas.ellipse(
            (ring_x, ring_y, ring_x + ring_r, ring_y + ring_r),
            fill=(255, 215, 0, 90),
            outline=(255, 255, 255, 255),
            width=8
        )

        canvas.paste(img_sq, (x_pos, y_pos), mask)
        canvas.save(output_path, "PNG")
        return output_path
