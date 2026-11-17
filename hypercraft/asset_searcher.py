"""
hypercraft/asset_searcher.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Automated Entity Visual Search & Reference Asset Generator.
Searches Wikipedia/Wikimedia, Unsplash, and Bing for entities mentioned in dialogue,
downloads crisp high-resolution portraits, and crafts high-impact circular reference badges
with glowing gold/cyan borders, soft drop shadows, smart face-centered framing, and typography pills.
"""

import os
import re
import urllib.request
import urllib.parse
import json
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import cv2

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
ASSET_CACHE_DIR = os.path.join(ROOT_DIR, "clips", "asset_cache")
os.makedirs(ASSET_CACHE_DIR, exist_ok=True)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

WIKI_HEADERS = {
    "User-Agent": "HyperCraftVisualBot/5.0 (https://github.com/stealthcoach; contact@stealthcoach.ai)"
}


def _download_url(url: str, output_path: str) -> bool:
    """Downloads an image URL with proper browser headers and validation."""
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if len(data) > 3000:
                with open(output_path, "wb") as f:
                    f.write(data)
                # Verify that it is a valid image
                with Image.open(output_path) as im:
                    im.verify()
                return True
    except Exception as e:
        print(f"[!] Download error for {url}: {e}")
    return False


def _detect_face_center_ratio(img_path: str) -> float:
    """
    Uses OpenCV Haar Cascade face detector to locate the primary face and return
    its vertical center ratio (0.0 = top, 1.0 = bottom) for smart portrait cropping.
    """
    default_ratio = 0.32
    try:
        cv_img = cv2.imread(img_path)
        if cv_img is None:
            return default_ratio
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if not os.path.exists(cascade_path):
            return default_ratio
        cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
        if len(faces) > 0:
            # Sort by area descending to find dominant face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            fx, fy, fw, fh = faces[0]
            face_center_y = fy + (fh * 0.45)
            ratio = face_center_y / cv_img.shape[0]
            return max(0.18, min(0.60, float(ratio)))
    except Exception:
        pass
    return default_ratio


def search_entity_image(query: str, force_refresh: bool = False) -> str | None:
    """
    Finds a pristine, crisp portrait or reference image for an entity.
    Returns the path to the rendered circular badge PNG.
    """
    clean_q = re.sub(r"[^a-zA-Z0-9\s]", "", query).strip()
    if not clean_q:
        return None

    safe_name = clean_q.lower().replace(" ", "_")
    badge_path = os.path.join(ASSET_CACHE_DIR, f"{safe_name}.png")
    named_badge_path = os.path.join(ASSET_CACHE_DIR, f"badge_{safe_name}.png")
    raw_download = os.path.join(ASSET_CACHE_DIR, f"raw_{safe_name}.jpg")

    # If raw image already exists and is valid, directly generate/return badge
    if not force_refresh and os.path.exists(raw_download) and os.path.getsize(raw_download) > 5000:
        create_circular_badge(raw_download, badge_path, clean_q.upper())
        create_circular_badge(raw_download, named_badge_path, clean_q.upper())
        return badge_path

    # 1. Wikipedia Direct Title Query (Crisp 1000px thumbnail)
    try:
        title_norm = urllib.parse.quote(clean_q.replace(" ", "_"))
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&titles={title_norm}"
            f"&prop=pageimages&format=json&pithumbsize=1000"
        )
        req = urllib.request.Request(url, headers=WIKI_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for _, p in pages.items():
                if "thumbnail" in p:
                    img_url = p["thumbnail"]["source"]
                    if _download_url(img_url, raw_download):
                        create_circular_badge(raw_download, badge_path, clean_q.upper())
                        create_circular_badge(raw_download, named_badge_path, clean_q.upper())
                        return badge_path
    except Exception as e:
        print(f"[!] Direct Wikipedia title search failed for '{clean_q}': {e}")

    # 2. Wikipedia Search Generator (fallback for variations/nicknames)
    try:
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&format=json"
            f"&prop=pageimages&pithumbsize=1000&generator=search"
            f"&gsrsearch={urllib.parse.quote(clean_q)}&gsrlimit=5"
        )
        req = urllib.request.Request(url, headers=WIKI_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for _, p in pages.items():
                if "thumbnail" in p:
                    img_url = p["thumbnail"]["source"]
                    if _download_url(img_url, raw_download):
                        create_circular_badge(raw_download, badge_path, clean_q.upper())
                        create_circular_badge(raw_download, named_badge_path, clean_q.upper())
                        return badge_path
    except Exception as e:
        print(f"[!] Wikipedia generator search failed for '{clean_q}': {e}")

    # 3. Bing Image Search Fallback
    try:
        bing_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(clean_q + ' portrait hd')}&FORM=HDRSC2"
        req = urllib.request.Request(bing_url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', html)
            for m in matches:
                if m.endswith((".jpg", ".png", ".jpeg", ".webp")):
                    if _download_url(m, raw_download):
                        create_circular_badge(raw_download, badge_path, clean_q.upper())
                        create_circular_badge(raw_download, named_badge_path, clean_q.upper())
                        return badge_path
    except Exception as e:
        print(f"[!] Bing search fallback failed for '{clean_q}': {e}")

    return None


def create_circular_badge(
    src_image: str,
    output_path: str,
    label: str = "CRISTIANO RONALDO",
    diameter: int = 380,
    theme: str = "gold",
    center_x: int = 540,
    center_y: int = 1340,
    full_canvas: bool = True
) -> str:
    """
    Transforms a raw photo into a viral, floating circular reference badge
    matching top YouTube Shorts (e.g. https://www.youtube.com/shorts/L9IGhWkwpgo):
      - Smart Face Detection vertical alignment
      - Deep soft drop shadow
      - Concentric neon gold/cyan glowing halo
      - High-contrast gold & white double outer ring
      - Crisp circular alpha portrait cutout (anti-aliased)
      - Glassmorphism entity label pill with bold typography
      - 1080x1920 transparent overlay canvas for instant FFmpeg 0:0 compositing
    """
    # Guard against passing an already generated canvas or badge as src_image
    actual_src = src_image
    if not os.path.exists(actual_src):
        raise FileNotFoundError(f"Source image not found: {actual_src}")

    # Check if the file passed is already an overlay canvas (1080x1920)
    with Image.open(actual_src) as check_im:
        if check_im.size == (1080, 1920):
            # Attempt to locate the raw download sibling
            base_stem = os.path.basename(actual_src).replace("badge_", "").replace(".png", "")
            raw_cand = os.path.join(ASSET_CACHE_DIR, f"raw_{base_stem}.jpg")
            if os.path.exists(raw_cand):
                actual_src = raw_cand
            else:
                for ext in [".png", ".webp", ".jpeg"]:
                    c = os.path.join(ASSET_CACHE_DIR, f"raw_{base_stem}{ext}")
                    if os.path.exists(c):
                        actual_src = c
                        break

    # 1. Smart face alignment ratio
    face_y_ratio = _detect_face_center_ratio(actual_src)

    # 2. Crop & Supersample Portrait
    with Image.open(actual_src).convert("RGBA") as raw_img:
        scale_factor = 2
        hi_res_dim = diameter * scale_factor

        img_sq = ImageOps.fit(
            raw_img,
            (hi_res_dim, hi_res_dim),
            centering=(0.5, face_y_ratio)
        )

        # Crisp supersampled circular mask
        mask_hi = Image.new("L", (hi_res_dim, hi_res_dim), 0)
        d_mask = ImageDraw.Draw(mask_hi)
        d_mask.ellipse((0, 0, hi_res_dim, hi_res_dim), fill=255)
        img_sq.putalpha(mask_hi)

        badge_portrait = img_sq.resize((diameter, diameter), Image.Resampling.LANCZOS)

    # Theme colors
    if theme == "cyan":
        glow_rgb = (6, 182, 212)
        ring_rgb = (6, 182, 212)
        pill_border = (6, 182, 212)
    else:  # gold
        glow_rgb = (255, 215, 0)
        ring_rgb = (255, 215, 0)
        pill_border = (255, 215, 0)

    # 3. Canvas Construction
    canvas_w, canvas_h = (1080, 1920) if full_canvas else (diameter + 120, diameter + 160)
    cx = center_x if full_canvas else canvas_w // 2
    cy = center_y if full_canvas else (diameter // 2 + 50)
    bx0 = cx - diameter // 2
    by0 = cy - diameter // 2

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    # 4. Soft Drop Shadow
    shadow_pad = 48
    shadow_dim = diameter + shadow_pad * 2
    shadow_layer = Image.new("RGBA", (shadow_dim, shadow_dim), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    s_draw.ellipse(
        (shadow_pad, shadow_pad + 14, shadow_pad + diameter, shadow_pad + diameter + 14),
        fill=(0, 0, 0, 190)
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(18))
    canvas.paste(shadow_layer, (cx - shadow_dim // 2, cy - shadow_dim // 2), shadow_layer)

    # 5. Glowing Outer Halo
    glow_layer = Image.new("RGBA", (shadow_dim, shadow_dim), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)
    for r_off in range(20, 0, -3):
        alpha = int(140 * (1.0 - r_off / 22.0))
        c = (*glow_rgb, alpha)
        g_draw.ellipse(
            (shadow_pad - r_off, shadow_pad - r_off, shadow_pad + diameter + r_off, shadow_pad + diameter + r_off),
            outline=c,
            width=3
        )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(glow_layer, (cx - shadow_dim // 2, cy - shadow_dim // 2), glow_layer)

    # 6. Outer Double Ring (Gold/Cyan + Crisp Inner White Line)
    ring_pad = 24
    ring_dim = diameter + ring_pad
    ring_layer = Image.new("RGBA", (ring_dim, ring_dim), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(ring_layer)
    r_draw.ellipse(
        (8, 8, ring_dim - 8, ring_dim - 8),
        outline=(*ring_rgb, 255),
        width=7
    )
    r_draw.ellipse(
        (11, 11, ring_dim - 11, ring_dim - 11),
        outline=(255, 255, 255, 230),
        width=2
    )
    canvas.paste(ring_layer, (cx - ring_dim // 2, cy - ring_dim // 2), ring_layer)

    # 7. Paste Portrait Cutout
    canvas.paste(badge_portrait, (bx0, by0), badge_portrait)

    # 8. Entity Label Pill Badge
    font_path = "C:\\Windows\\Fonts\\impact.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf"

    font_size = 26
    try:
        pill_font = ImageFont.truetype(font_path, font_size)
    except Exception:
        pill_font = ImageFont.load_default()

    clean_label = label.upper().strip()
    bbox = pill_font.getbbox(clean_label)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pw = max(tw + 48, 160)
    ph = 48
    px0 = cx - pw // 2
    py0 = cy + diameter // 2 - 16

    # Pill drop shadow
    pill_s = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0))
    ps_draw = ImageDraw.Draw(pill_s)
    ps_draw.rounded_rectangle((12, 14, pw + 12, ph + 14), radius=16, fill=(0, 0, 0, 160))
    pill_s = pill_s.filter(ImageFilter.GaussianBlur(6))
    canvas.paste(pill_s, (px0 - 12, py0 - 12), pill_s)

    # Pill glass body & border
    pill_draw = ImageDraw.Draw(canvas)
    pill_draw.rounded_rectangle(
        (px0, py0, px0 + pw, py0 + ph),
        radius=14,
        fill=(15, 23, 42, 248),
        outline=(*pill_border, 255),
        width=3
    )

    # Pill text with subtle shadow
    tx = px0 + (pw - tw) // 2
    ty = py0 + (ph - th) // 2 - 3
    pill_draw.text((tx + 2, ty + 2), clean_label, font=pill_font, fill=(0, 0, 0, 200))
    pill_draw.text((tx, ty), clean_label, font=pill_font, fill=(255, 255, 255, 255))

    # Save output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    canvas.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    print("[*] Testing asset_searcher on 'Cristiano Ronaldo'...")
    res = search_entity_image("Cristiano Ronaldo", force_refresh=True)
    print(f" -> Badge generated at: {res} (Exists: {os.path.exists(res) if res else False})")
    badge_path = os.path.join(ASSET_CACHE_DIR, "badge_ronaldo.png")
    create_circular_badge(res, badge_path, "CRISTIANO RONALDO", diameter=360)
    print(f" -> Named Badge generated at: {badge_path} (Size: {os.path.getsize(badge_path)} bytes)")
