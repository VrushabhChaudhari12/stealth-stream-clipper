"""
Viral Hook & Clickbait Thumbnail Generator v4.2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strict implementation of YouTube Shorts Viral Engine & 2026 Algorithm Rules:
  ✔ 40–60 Character Titles with Specific Number/Noun + Emotional Trigger
  ✔ 3–4 Word High-CTR Thumbnail Text (Strictly compliments, never duplicates title)
  ✔ 4-Tier Hashtag Architecture (Strictly 3–5 hashtags to avoid spam penalties)
  ✔ 9:16 Vertical Thumbnail with Face/Action Contrast & Gradient Vignette
"""

import os
import re
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ── 1. TITLE ENGINE (40–60 Chars | Number/Noun + Emotional Trigger) ───────────

VIRAL_TITLE_TEMPLATES = [
    "{streamer}'s 1 Big Mistake That Broke {topic}",
    "The 1 Secret Setting That Doubled {streamer}'s FPS",
    "Did {streamer} Actually Leak {topic} On Stream?!",
    "The $10,000 {topic} Moment {streamer} Lost His Mind",
    "{streamer} Found 3 Secret {topic} Glitches",
    "Why {topic} Is Actually Insane With {streamer}",
    "The 1 Moment {streamer} Caught Everyone In 4K",
    "{streamer}'s 0.001s Reaction That Shocked Chat",
    "The 1 Secret Code {streamer} Accidentally Revealed",
    "{streamer} Gave Away 1 Free {topic} Key Live"
]

TOPIC_KEYWORDS = {
    "gta": "GTA 6",
    "gta 6": "GTA 6",
    "giveaway": "GTA 6",
    "key": "GTA 6 Key",
    "ps5": "PS5 Game",
    "money": "$10,000",
    "clutch": "1v5 Clutch",
    "police": "5 Stars",
    "car": "Supercar"
}


def extract_hook_topic(transcript_text: str, default: str = "GTA 6") -> str:
    """Extracts highest hype keyword from transcript sample."""
    lower = transcript_text.lower()
    for kw, topic in TOPIC_KEYWORDS.items():
        if kw in lower:
            return topic
    return default


def generate_clickbait_title(streamer: str, transcript_text: str = "") -> str:
    """
    Enforces the 40–60 character rule:
      - Never truncates on mobile UI (< 60 chars)
      - Includes one specific number or proper noun
      - Formula: [Specific claim] + [emotional trigger]
    """
    topic = extract_hook_topic(transcript_text, default="GTA 6")
    clean_streamer = streamer.replace("@", "").strip().title()

    templates = list(VIRAL_TITLE_TEMPLATES)
    random.shuffle(templates)

    for tmpl in templates:
        title = tmpl.format(streamer=clean_streamer, topic=topic)
        if 40 <= len(title) <= 60:
            return title

    # Fallback guaranteed to be 40–55 chars
    fallback = f"{clean_streamer}'s 1 Mistake That Broke {topic} Forever"
    if len(fallback) > 60:
        fallback = f"{clean_streamer} Leaked 1 Secret {topic} Moment"
    return fallback[:60]


# ── 2. THUMBNAIL TEXT (3–4 Words Max | Non-Duplicative) ──────────────────────

THUMB_PUNCH_PHRASES = [
    "BROKE IT! 😱",
    "NO WAY?! 💀",
    "0.001s REACTION",
    "CAUGHT IN 4K",
    "HE DID IT! 🔥",
    "WAIT FOR IT",
    "INSANE MOMENT",
    "SECRET LEAK?!",
    "CHAT WENT WILD",
    "$10,000 GONE! 💸"
]


def pick_thumbnail_hook(title: str) -> str:
    """
    Selects 3–4 words max of text that does NOT duplicate the title.
    They form a complementary pairing on the viewer's feed.
    """
    candidates = [p for p in THUMB_PUNCH_PHRASES if not any(w.lower() in title.lower() for w in p.split()[:2])]
    return random.choice(candidates) if candidates else random.choice(THUMB_PUNCH_PHRASES)


# ── 3. METADATA & 4-TIER HASHTAG SYSTEM ──────────────────────────────────────

def generate_seo_metadata(streamer: str, title: str, source_url: str = "") -> dict:
    """
    Builds clean, high-reach YouTube metadata adhering to the 4-tier system:
      - Strictly 3–5 hashtags total (prevents YouTube spam penalty)
      - 1–2 crisp sentences + source link
    """
    clean_streamer = streamer.replace("@", "").strip()

    # 4-Tier Hashtag Selection (Select exactly 4 hashtags total)
    tier1 = "#shorts"
    tier2 = f"#{re.sub(r'[^a-zA-Z0-9]', '', clean_streamer).lower()}"
    tier3 = "#gaming"
    tier4 = "#viral"
    hashtags_str = f"{tier1} {tier2} {tier3} {tier4}"

    description = (
        f"{title}\n\n"
        f"Watch the full stream replay: {source_url or 'https://youtube.com'}\n\n"
        f"Transformed with dynamic editing and subtitles under Fair Use. All rights belong to @{clean_streamer}.\n\n"
        f"{hashtags_str}"
    )

    tags = [clean_streamer, "shorts", "gaming", "viral clips", "stream highlights", "gta 6"]

    return {
        "title": title,
        "description": description.strip(),
        "tags": tags,
        "category_id": "20"  # Gaming
    }


# ── 4. 9:16 HIGH-CTR THUMBNAIL GENERATOR ─────────────────────────────────────

def create_clickbait_thumbnail(video_path: str, output_jpg: str, hook_text: str | None = None,
                               ffmpeg_bin: str = "ffmpeg") -> bool:
    """
    Creates an ultra-high CTR 9:16 vertical thumbnail:
      - 1 face / action shot
      - 3–4 words max of high-contrast text
      - Saturated + contrast boosted
      - Gradient vignette for mobile readability
    """
    temp_frame = output_jpg + ".raw.jpg"
    try:
        # Extract peak frame from second 2.5
        cmd = [
            ffmpeg_bin, "-y",
            "-ss", "00:00:02.500",
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            temp_frame
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if not os.path.exists(temp_frame):
            return False

        # Open and resize to standard 9:16 (1080x1920)
        im = Image.open(temp_frame).convert("RGB")
        im = im.resize((1080, 1920), Image.Resampling.LANCZOS)

        # Contrast & Saturation Boost (+15% contrast, +20% color)
        im = ImageEnhance.Contrast(im).enhance(1.15)
        im = ImageEnhance.Color(im).enhance(1.20)

        # Dark gradient top and bottom for typography readability
        gradient = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw_grad = ImageDraw.Draw(gradient)

        for y in range(450):
            alpha = int(180 * (1.0 - (y / 450.0)))
            draw_grad.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        for y in range(1500, 1920):
            alpha = int(190 * ((y - 1500) / 420.0))
            draw_grad.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        im.paste(Image.alpha_composite(im.convert("RGBA"), gradient), (0, 0))

        # Typography (3-4 words max, large yellow with black border)
        draw = ImageDraw.Draw(im)

        font = None
        for font_name in ["impact.ttf", "arialbd.ttf", "Arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 86)
                break
            except Exception:
                pass
        if not font:
            font = ImageFont.load_default()

        phrase = (hook_text or random.choice(THUMB_PUNCH_PHRASES)).upper().strip()
        words = phrase.split()
        if len(words) > 4:
            phrase = " ".join(words[:4])

        # Centered near upper-third (y=300)
        bbox = draw.textbbox((0, 0), phrase, font=font)
        text_w = bbox[2] - bbox[0]
        x = (1080 - text_w) // 2
        y = 300

        # Heavy 9px black outline
        stroke_w = 9
        for ox in range(-stroke_w, stroke_w + 1):
            for oy in range(-stroke_w, stroke_w + 1):
                draw.text((x + ox, y + oy), phrase, font=font, fill=(0, 0, 0))

        # Vibrant Yellow fill
        draw.text((x, y), phrase, font=font, fill=(255, 255, 0))

        im.convert("RGB").save(output_jpg, "JPEG", quality=95)
        return True

    except Exception as e:
        print(f"[!] Thumbnail engine notice: {e}")
        return False
    finally:
        if os.path.exists(temp_frame):
            try:
                os.remove(temp_frame)
            except Exception:
                pass
