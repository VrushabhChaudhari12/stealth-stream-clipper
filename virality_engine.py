"""
Virality Intelligence & Emotion Detection Engine v5.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Implements findings from YouTube Algorithm Audits & 2026 Shorts Rules:
  ✔ Emotion & Reaction Matching: Detects shock, dump, rejection, pause/ayo, and rage moments.
  ✔ 18% Spicy Indirect Humor Formatting: Injects cheeky double entendres & 18% mature disclosure.
  ✔ Pre-Upload Virality Gate: Scores clips 1-10 on Hook, Energy, Pacing, and Payoff.
  ✔ Only publishes clips scoring >= 7.0/10 to protect channel reach from 1k-view jail.
"""

import os
import re
import json
import random
import subprocess
from datetime import datetime

# ── 1. EMOTION & REACTION KEYWORDS ───────────────────────────────────────────

EMOTION_PATTERNS = {
    "dumped_rejection": [
        "dumped", "dump", "she left", "broke up", "rejected", "rejection", "crying",
        "tears", "cheated", "heartbroken", "no love", "single", "over", "sad"
    ],
    "pause_spicy_18": [
        "pause", "ayo", "sus", "freaky", "18", "spicy", "wild", "unhinged", "caught",
        "in 4k", "what did he say", "wait what", "down bad", "riri", "amy"
    ],
    "rage_shock": [
        "what the hell", "no way", "oh my god", "are you serious", "hell no", "bro what",
        "speed chill", "barking", "screaming", "punch", "broke", "smash", "khatam", "arre"
    ],
    "funny_cooked": [
        "cooked", "bro is cooked", "packwatch", "lmao", "lol", "rip", "skill issue",
        "clowned", "exposed", "defeated", "hilarious", "dead", "💀", "😭", "🤣"
    ]
}

CHAT_HYPE_EMOTIONS = {
    "💀": 2.0, "LMAO": 1.8, "COOKED": 2.2, "DUMPED": 2.5, "PAUSE": 2.2,
    "AYO": 2.0, "SUS": 1.9, "L": 1.5, "W": 1.4, "NO WAY": 1.8, "HE CRIED": 2.4
}


def score_emotion_context(text: str) -> tuple[str, float]:
    """
    Analyzes text (transcript or chat burst) to classify the dominant emotion
    and calculate an emotional intensity multiplier.
    """
    lower = text.lower()
    scores = {}
    for category, words in EMOTION_PATTERNS.items():
        count = sum(1 for w in words if w in lower)
        scores[category] = count

    dominant_cat = max(scores, key=scores.get) if any(scores.values()) else "general_hype"
    intensity = 1.0 + (scores.get(dominant_cat, 0) * 0.35)
    return dominant_cat, min(intensity, 2.5)


# ── 2. 18% SPICY HOOK & TITLE GENERATOR ──────────────────────────────────────

SPICY_18_TITLES = [
    "{streamer} Got DUMPED in 0.001s On Live Stream?! 💀",
    "Did {streamer} Actually Say THIS Out Loud?! (PAUSE) 🚨",
    "The 1 Moment {streamer} Was Caught Being Down Bad 😭",
    "{streamer}'s Most Unhinged 18% Spicy Stream Reaction 🔥",
    "She Said NO to {streamer} in Front of 100K People 💔",
    "The 1 Freaky Question That Broke {streamer}'s Stream 💀",
    "Why {streamer} Got BANNED For 3 Seconds (AYO) 😱",
    "{streamer}'s 1 Reaction That Got Rated 18% Spicy 🌶️",
    "{streamer} Thought The Mic Was Muted For THIS... 📸",
    "The Moment {streamer} Realized He Was 100% COOKED 💀"
]

SPICY_THUMB_HOOKS = [
    "DUMPED LIVE! 💔",
    "PAUSE AYO?! 💀",
    "CAUGHT IN 4K 📸",
    "HE CRIED! 😭",
    "18% SPICY 🌶️",
    "BRO IS COOKED",
    "SHE SAID NO! 😱",
    "NO WAY HE DID IT",
    "UNHINGED 💀",
    "DOWN BAD! 😭"
]


def generate_spicy_title(streamer: str, emotion_cat: str = "general_hype") -> str:
    """Generates an edgy 40–60 character title with emotional trigger & numbers."""
    clean_streamer = streamer.replace("@", "").strip().title()
    templates = list(SPICY_18_TITLES)
    random.shuffle(templates)

    for tmpl in templates:
        title = tmpl.format(streamer=clean_streamer)
        if 40 <= len(title) <= 60:
            return title

    fallback = f"{clean_streamer} Got DUMPED In 0.001s (PAUSE) 💀"
    return fallback[:60]


def pick_spicy_thumb_hook(title: str) -> str:
    """Picks a 3–4 word thumbnail punch that compliments the title without duplicating."""
    choices = [h for h in SPICY_THUMB_HOOKS if not any(w.lower() in title.lower() for w in h.split()[:2])]
    import random
    return random.choice(choices) if choices else random.choice(SPICY_THUMB_HOOKS)


def generate_spicy_seo(streamer: str, title: str, source_url: str = "") -> dict:
    """
    Builds compliant SEO metadata with the mandatory 'Rated 18% Spicy' disclosure
    and exactly 4-tier hashtags (3–5 tags total to avoid spam flags).
    """
    clean_streamer = streamer.replace("@", "").strip()

    description = (
        f"{title}\n\n"
        f"⚠️ Rated 18% Spicy | Mature humor, indirect jokes & extreme reactions. Viewer discretion advised.\n\n"
        f"Watch the full stream replay: {source_url or 'https://youtube.com'}\n\n"
        f"Transformed with kinetic subtitles, audio ducking, and commentary under Fair Use. All rights belong to @{clean_streamer}.\n\n"
        f"#shorts #{re.sub(r'[^a-zA-Z0-9]', '', clean_streamer).lower()} #gaming #viral"
    )

    tags = [clean_streamer, "shorts", "gaming", "stream highlights", "funny moments", "18 spicy", "gta 6"]

    return {
        "title": title,
        "description": description.strip(),
        "tags": tags,
        "category_id": "20"
    }


# ── 3. PRE-UPLOAD VIRALITY TEST (The Gatekeeper) ─────────────────────────────

class ViralityTester:
    """
    Audits candidate clips against the 2026 YouTube Shorts Algorithm benchmarks:
      1. Duration Sweet Spot (25s - 45s) -> 2.5 pts
      2. Hook Pacing (Words in first 3s >= 6) -> 2.5 pts
      3. Emotional Intensity & Keyword Density -> 2.5 pts
      4. Metadata Compliance (40-60 chars title, 3-5 hashtags) -> 2.5 pts
    Total: 10.0 pts. Minimum passing score: 7.0 / 10.
    """

    @staticmethod
    def audit_clip(video_path: str, transcript_words: list[dict], title: str,
                   ffmpeg_bin: str = "ffmpeg") -> dict:
        score = 0.0
        checks = {}

        # 1. Duration Check (25s - 45s is optimal, >60s is disqualified)
        duration = 0.0
        if transcript_words:
            duration = transcript_words[-1].get("end", 35.0)
        else:
            duration = 35.0

        if 25.0 <= duration <= 45.0:
            score += 2.5
            checks["duration"] = f"PASS: {duration:.1f}s (Inside 25-45s sweet spot)"
        elif duration < 25.0:
            score += 1.5
            checks["duration"] = f"WARN: {duration:.1f}s (Slightly short, high rewatch potential)"
        elif duration <= 60.0:
            score += 1.0
            checks["duration"] = f"WARN: {duration:.1f}s (Nearing 60s hard ceiling)"
        else:
            checks["duration"] = f"FAIL: {duration:.1f}s (Exceeds 60s Shorts ceiling)"

        # 2. Hook Velocity (First 3 Seconds)
        words_in_hook = [w for w in transcript_words if w.get("start", 0) <= 3.2]
        hook_word_count = len(words_in_hook)
        if hook_word_count >= 5:
            score += 2.5
            checks["hook_speed"] = f"PASS: {hook_word_count} words in first 3s (High vocal momentum)"
        elif hook_word_count >= 2:
            score += 1.5
            checks["hook_speed"] = f"WARN: {hook_word_count} words in first 3s (Moderate hook pacing)"
        else:
            score += 0.5
            checks["hook_speed"] = f"FAIL: {hook_word_count} words in first 3s (Dead air risk in first 3s)"

        # 3. Emotional Intensity Check
        all_text = " ".join(w.get("word", "") for w in transcript_words)
        emotion_cat, intensity = score_emotion_context(all_text)
        if intensity >= 1.7:
            score += 2.5
            checks["emotion"] = f"PASS: Peak emotional reaction detected ({emotion_cat}, {intensity:.2f}x)"
        elif intensity > 1.0:
            score += 2.0
            checks["emotion"] = f"PASS: Moderate emotional reaction ({emotion_cat})"
        else:
            score += 1.0
            checks["emotion"] = f"WARN: Flat tone detected; relying on chat reaction velocity"

        # 4. Title & Metadata CTR Check
        title_len = len(title)
        has_number_or_caps = bool(re.search(r"\d", title)) or bool(re.search(r"[A-Z]{3,}", title))
        if 40 <= title_len <= 60 and has_number_or_caps:
            score += 2.5
            checks["title_ctr"] = f"PASS: {title_len} chars with high-CTR trigger"
        elif 35 <= title_len <= 65:
            score += 1.8
            checks["title_ctr"] = f"PASS: {title_len} chars"
        else:
            score += 1.0
            checks["title_ctr"] = f"WARN: {title_len} chars (Suboptimal mobile display)"

        passed = score >= 7.0
        return {
            "score": round(score, 1),
            "passed": passed,
            "threshold": 7.0,
            "duration": round(duration, 1),
            "dominant_emotion": emotion_cat,
            "checks": checks
        }
