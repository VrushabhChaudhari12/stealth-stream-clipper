"""
hypercraft/motion_crafter.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HyperFrames & Remotion style declarative motion graphics generator.
Renders high-fidelity kinetic HUD cards, retention graphs,
and visual callouts with glassmorphism and glowing borders.
"""

import os
from PIL import Image, ImageDraw, ImageFont

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
ASSETS_DIR = os.path.join(ROOT_DIR, "clips", "hypercraft_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

THEME_COLORS = {
    "danger": {
        "border": (239, 68, 68, 255),      # Neon Red #ef4444
        "glow": (239, 68, 68, 60),
        "badge_bg": (185, 28, 28, 240),
        "text": (255, 255, 255, 255),
        "accent": (254, 202, 202, 255)
    },
    "metric": {
        "border": (6, 182, 212, 255),       # Neon Cyan #06b6d4
        "glow": (6, 182, 212, 60),
        "badge_bg": (14, 116, 144, 240),
        "text": (255, 255, 255, 255),
        "accent": (165, 243, 252, 255)
    },
    "warning": {
        "border": (245, 158, 11, 255),     # Neon Amber #f59e0b
        "glow": (245, 158, 11, 60),
        "badge_bg": (180, 83, 9, 240),
        "text": (255, 255, 255, 255),
        "accent": (253, 230, 138, 255)
    },
    "success": {
        "border": (16, 185, 129, 255),     # Neon Emerald #10b981
        "glow": (16, 185, 129, 60),
        "badge_bg": (4, 120, 87, 240),
        "text": (255, 255, 255, 255),
        "accent": (167, 243, 208, 255)
    }
}


def get_font(size: int, bold: bool = True):
    font_names = [
        "C:\\Windows\\Fonts\\montserrat_black.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf"
    ]
    for path in font_names:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_kinetic_hud_card(card: dict, output_path: str) -> str:
    """
    Renders a 1080x1920 transparent PNG with a glassmorphism floating card.
    Positioned in the upper-middle area (y: 280-480) above gameplay and captions.
    """
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    theme = THEME_COLORS.get(card.get("theme", "metric"), THEME_COLORS["metric"])
    title = card.get("title", "ALGORITHM INTEL")
    keyword = card.get("keyword", "DATA")

    # Card dimensions
    card_w = 880
    card_h = 220
    x0 = (1080 - card_w) // 2
    y0 = 320
    x1 = x0 + card_w
    y1 = y0 + card_h

    # 1. Outer Glow
    for offset in range(6, 0, -2):
        draw.rounded_rectangle(
            [x0 - offset, y0 - offset, x1 + offset, y1 + offset],
            radius=24,
            fill=theme["glow"]
        )

    # 2. Glassmorphism dark body
    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=20,
        fill=(15, 23, 42, 235),  # Slate-900 with 92% opacity
        outline=theme["border"],
        width=4
    )

    # 3. Top category badge
    badge_w = 420
    badge_h = 44
    bx0 = x0 + 30
    by0 = y0 + 24
    draw.rounded_rectangle(
        [bx0, by0, bx0 + badge_w, by0 + badge_h],
        radius=10,
        fill=theme["badge_bg"]
    )
    badge_font = get_font(24, bold=True)
    draw.text((bx0 + 16, by0 + 8), title, font=badge_font, fill=(255, 255, 255, 255))

    # 4. Main Metric / Keyword Text
    keyword_font = get_font(56, bold=True)
    draw.text((x0 + 32, y0 + 84), keyword, font=keyword_font, fill=theme["accent"])

    # 5. Tech Ticker / Micro-label
    sub_font = get_font(22, bold=False)
    draw.text((x0 + 34, y0 + 162), "SYSTEM: 2026 AUDIENCE VECTOR MATCHING", font=sub_font, fill=(148, 163, 184, 255))

    # 6. Retention curve sparkline on the right
    spark_x = x1 - 220
    spark_y = y0 + 90
    points = [
        (spark_x, spark_y + 60),
        (spark_x + 40, spark_y + 10),
        (spark_x + 80, spark_y + 45),
        (spark_x + 130, spark_y + 20),
        (spark_x + 180, spark_y + 5)
    ]
    draw.line(points, fill=theme["border"], width=4)
    for px, py in points:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255, 255))

    img.save(output_path, "PNG")
    return output_path


def render_retention_graph_overlay(output_path: str) -> str:
    """
    Renders an interactive animated retention graph card explaining the 200-view drop.
    """
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Card dimensions
    card_w = 900
    card_h = 320
    x0 = (1080 - card_w) // 2
    y0 = 300
    x1 = x0 + card_w
    y1 = y0 + card_h

    # Card background
    draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(15, 23, 42, 240), outline=(239, 68, 68, 255), width=4)

    # Title
    font_title = get_font(30, bold=True)
    draw.text((x0 + 30, y0 + 24), "📉 THE 200-VIEW CLIFF (RETENTION CRASH)", font=font_title, fill=(255, 255, 255, 255))

    # Axis lines
    gx0 = x0 + 60
    gy0 = y0 + 90
    gx1 = x1 - 60
    gy1 = y1 - 50
    draw.line([(gx0, gy1), (gx1, gy1)], fill=(71, 85, 105, 255), width=2)
    draw.line([(gx0, gy0), (gx0, gy1)], fill=(71, 85, 105, 255), width=2)

    # Steep drop-off curve (Standard failed short)
    drop_points = [
        (gx0, gy0 + 10),
        (gx0 + 80, gy0 + 20),
        (gx0 + 160, gy1 - 30),  # Steep fall at 2 seconds
        (gx0 + 350, gy1 - 10),
        (gx1, gy1 - 5)
    ]
    draw.line(drop_points, fill=(239, 68, 68, 255), width=5)

    # Viral loop curve (Passed short)
    viral_points = [
        (gx0, gy0 + 10),
        (gx0 + 120, gy0 + 15),
        (gx0 + 300, gy0 + 35),
        (gx0 + 550, gy0 + 40),
        (gx1, gy0 + 10)  # Re-loops at 100%+
    ]
    draw.line(viral_points, fill=(16, 185, 129, 255), width=4)

    # Legend
    font_legend = get_font(20, bold=True)
    draw.text((gx0 + 400, y0 + 30), "■ VIRAL LOOP (>100%)", font=font_legend, fill=(16, 185, 129, 255))

    img.save(output_path, "PNG")
    return output_path
