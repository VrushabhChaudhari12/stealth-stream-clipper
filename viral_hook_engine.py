"""
Viral Hook & Clickbait Thumbnail Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates high-CTR YouTube Shorts hooks, clickbait titles, and 9:16 vertical thumbnails.
Inspired by openshorts (mutonby) & OpenMontage frameworks.
"""

import os
import re
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ── Viral Clickbait Title Templates ──────────────────────────────────────────
CLICKBAIT_TEMPLATES = [
    "{streamer} REVEALED {topic}?! 😱",
    "NO WAY {streamer} ACTUALLY SAID THIS... 💀",
    "{streamer} WENT CRAZY ON STREAM! 🔥",
    "THE MOMENT {streamer} LOST HIS MIND 😂",
    "WAIT... DID {streamer} JUST LEAK {topic}?! 🚨",
    "{streamer} CAUGHT IN 4K DOING THIS! 📸",
    "{streamer} GIVING AWAY {topic}?! 🎁",
    "EVERYONE SPAMMED 'W' FOR THIS! ⬆️🔥",
    "CHAT WENT COMPLETELY WILD HERE! 💀😭",
    "{streamer} HAD ZERO CHILL FOR THIS! ⚡"
]

TOPIC_KEYWORDS = {
    "gta": "GTA 6",
    "gta 6": "GTA 6",
    "giveaway": "GIVEAWAY",
    "key": "EXCLUSIVE KEY",
    "ps5": "PS5",
    "xbox": "XBOX",
    "money": "$10,000",
    "clutch": "1v5 CLUTCH",
    "rage": "RAGE QUIT",
    "police": "5 STARS",
    "car": "SUPERCAR"
}


def extract_hook_topic(transcript_text: str, default: str = "GTA 6") -> str:
    """Detects core high-hype topic from transcript text."""
    lower = transcript_text.lower()
    for kw, topic in TOPIC_KEYWORDS.items():
        if kw in lower:
            return topic
    return default


def generate_clickbait_title(streamer: str, transcript_text: str = "") -> str:
    """Generates high-CTR clickbait title optimized for YouTube Shorts (< 60 chars)."""
    topic = extract_hook_topic(transcript_text, default="THIS")
    clean_streamer = streamer.replace("@", "").strip()
    
    template = random.choice(CLICKBAIT_TEMPLATES)
    title = template.format(streamer=clean_streamer, topic=topic)
    
    # Ensure it fits mobile Shorts UI perfectly
    if len(title) > 65:
        title = f"{clean_streamer} REVEALED {topic}?! 😱"
    return title


def generate_seo_metadata(streamer: str, title: str, source_url: str = "") -> dict:
    """Builds keyword-optimized description and tags for YouTube reach."""
    clean_streamer = streamer.replace("@", "").strip()
    
    description = f"""{title}

🔥 Don't forget to LIKE & SUBSCRIBE for daily gaming clips and stream highlights!
Credits to @{clean_streamer} for the stream moment!

📺 Original Streamer: @{clean_streamer}
🔗 Source: {source_url}

=== Fair Use Notice ===
This clip was captured and transformed with commentary, dynamic formatting, and subtitles under Fair Use. All rights belong to @{clean_streamer}.

#shorts #gaming #{clean_streamer.lower()} #twitch #streamer #clips #viral #trending #gta6 #funny
"""
    tags = [
        clean_streamer,
        f"{clean_streamer} clips",
        f"{clean_streamer} funny moments",
        "gta 6",
        "gta 6 leak",
        "gaming shorts",
        "viral clips",
        "stream highlights",
        "funny gaming moments",
        "twitch highlights",
        "shorts"
    ]
    
    return {
        "title": title,
        "description": description.strip(),
        "tags": tags,
        "category_id": "20"  # Gaming
    }


# ── 9:16 High-CTR Thumbnail Generator ────────────────────────────────────────

def create_clickbait_thumbnail(video_path: str, output_jpg: str, hook_text: str, ffmpeg_bin: str = "ffmpeg"):
    """
    Extracts a peak action frame, applies contrast enhancement, dark gradient vignette,
    and burns high-impact clickbait text in giant yellow/white typography.
    """
    temp_frame = output_jpg + ".raw.jpg"
    try:
        # 1. Grab frame from 2.5s into the video (avoids black intro frames)
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

        # 2. Open image in Pillow
        im = Image.open(temp_frame).convert("RGB")
        im = im.resize((1080, 1920), Image.Resampling.LANCZOS)

        # 3. Apply Visual Punch (Contrast + Saturation Boost)
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Color(im)
        im = enhancer.enhance(1.20)

        # 4. Top & Bottom Dark Gradient Overlay (for text readability)
        gradient = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw_grad = ImageDraw.Draw(gradient)
        
        # Top vignette
        for y in range(450):
            alpha = int(180 * (1.0 - (y / 450.0)))
            draw_grad.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
            
        # Bottom vignette
        for y in range(1500, 1920):
            alpha = int(190 * ((y - 1500) / 420.0))
            draw_grad.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        im.paste(Image.alpha_composite(im.convert("RGBA"), gradient), (0, 0))

        # 5. Burn Hook Text (Bold Yellow + Thick Black Stroke)
        draw = ImageDraw.Draw(im)
        
        # Try loading Arial or system bold font
        font = None
        for font_name in ["impact.ttf", "arialbd.ttf", "Arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 76)
                break
            except Exception:
                pass
        if not font:
            font = ImageFont.load_default()

        # Word wrap text into 2-3 lines max
        words = hook_text.upper().split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 14:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        # Draw lines centered near the upper third (y=280)
        start_y = 280
        for line in lines[:3]:
            # Bounding box
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (1080 - w) // 2

            # Black border (8px stroke)
            stroke_w = 8
            for ox in range(-stroke_w, stroke_w + 1):
                for oy in range(-stroke_w, stroke_w + 1):
                    draw.text((x + ox, start_y + oy), line, font=font, fill=(0, 0, 0))

            # Vibrant Yellow text
            draw.text((x, start_y), line, font=font, fill=(255, 255, 0))
            start_y += 90

        # Save finalized thumbnail
        im.convert("RGB").save(output_jpg, "JPEG", quality=95)
        return True

    except Exception as e:
        print(f"[!] Thumbnail generation error: {e}")
        return False
    finally:
        if os.path.exists(temp_frame):
            try:
                os.remove(temp_frame)
            except Exception:
                pass
