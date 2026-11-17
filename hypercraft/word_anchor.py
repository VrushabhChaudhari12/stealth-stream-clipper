"""
hypercraft/word_anchor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hypit-inspired word-level event anchoring.
Scans Whisper word timestamps to bind kinetic visual HUD cards,
shot cuts, and sound effect triggers directly to spoken words.
Supports both viral education/algorithm content and gaming streamer clips.
"""

import re

from hypercraft.broll_engine import get_broll_for_keyword

TRIGGER_PATTERNS = [
    # Danger / Negative Hook / Shock triggers
    {
        "keywords": ["stop", "deleting", "never", "wrong", "mistake", "shadowbanned", "trapped", "jail", "terrified", "scared", "fear", "crazy", "insane", "what", "omg", "died", "treat"],
        "card_type": "ALERT_BADGE",
        "title": "⚠️ SHOCKWAVE ALERT",
        "theme": "danger",
        "sfx": "bass_hit",
        "zoom": 1.15
    },
    # Metric / Data / Number triggers
    {
        "keywords": ["200", "1k", "1000", "zero", "percent", "thirty", "half", "19", "names", "top", "six", "first"],
        "card_type": "DATA_METRIC",
        "title": "📊 STAT PEAK SPIKE",
        "theme": "metric",
        "sfx": "pop",
        "zoom": 1.10
    },
    # Motion / Action / Slam triggers
    {
        "keywords": ["swipe", "away", "kills", "scroll", "drop", "dead", "dunk", "funk", "double", "jump", "slam", "fast"],
        "card_type": "SWIPE_INDICATOR",
        "title": "⚡ SLAM DUNK IMPACT",
        "theme": "warning",
        "sfx": "whoosh",
        "zoom": 1.14
    },
    # Payoff / Flex / Goat / Solution triggers
    {
        "keywords": ["escape", "fix", "secret", "hack", "loop", "solution", "scale", "portuguese", "ronaldo", "goat", "worlds", "win", "clutch", "clean", "nice", "speed"],
        "card_type": "UNLOCK_CARD",
        "title": "🏆 WORLD CLASS GOAT",
        "theme": "success",
        "sfx": "alert",
        "zoom": 1.12
    }
]


def anchor_words_to_events(words: list[dict], total_duration: float) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """
    Parses Whisper word timestamps.
    Returns:
      - visual_cards: list of kinetic HUD cards to render on screen
      - sfx_cues: list of audio sound effects synchronized to words
      - camera_moves: list of shot zoom/pan intervals
      - broll_cues: list of B-roll cutaway video clips
    """
    visual_cards = []
    sfx_cues = []
    camera_moves = []
    broll_cues = []

    # Always insert an opening hook camera push-in (0.0 to 2.5s)
    camera_moves.append({
        "start": 0.0,
        "end": min(2.8, total_duration),
        "start_zoom": 1.0,
        "end_zoom": 1.15,
        "type": "PUSH_IN"
    })
    sfx_cues.append({"type": "whoosh", "time": 0.05, "volume": 0.65})

    last_card_end = 0.0
    last_broll_end = 4.0  # Reserve 0-4s for opening hook without B-roll interruption

    for w in words:
        clean_word = re.sub(r"[^a-zA-Z0-9%]", "", w.get("word", "").lower())
        start_time = float(w.get("start", 0.0))
        end_time = float(w.get("end", start_time + 0.3))

        # Check for B-roll triggers
        if clean_word in ["algorithm", "jails", "trapped", "swipe", "percent", "kills", "worlds", "top", "fast", "speed"]:
            if start_time >= last_broll_end + 3.5 and start_time + 1.5 <= total_duration:
                broll_path = get_broll_for_keyword(clean_word)
                if broll_path:
                    broll_dur = 1.5
                    broll_cues.append({
                        "keyword": clean_word,
                        "path": broll_path,
                        "start": start_time,
                        "end": min(start_time + broll_dur, total_duration),
                        "duration": broll_dur
                    })
                    last_broll_end = start_time + broll_dur

        for pattern in TRIGGER_PATTERNS:
            if clean_word in pattern["keywords"]:
                # Ensure minimum 1.8s spacing between cards so they don't overlap
                if start_time >= last_card_end + 0.5 and start_time + 2.0 <= total_duration:
                    card_dur = 2.0
                    
                    # Custom dynamic title based on specific word
                    custom_title = pattern["title"]
                    if clean_word in ["portuguese", "ronaldo"]:
                        custom_title = "🇵🇹 RONALDO DNA ACTIVE"
                    elif clean_word in ["terrified", "fear"]:
                        custom_title = "😱 SPEED IS TERRIFIED"
                    elif clean_word in ["dunk", "funk"]:
                        custom_title = "🏀 SLAM DUNK PEAK"
                    elif clean_word in ["worlds", "top"]:
                        custom_title = "🌍 TOP 6 IN THE WORLD"
                    elif clean_word in ["19"]:
                        custom_title = "🔥 SPEED PEAK LEVEL 19"
                    elif clean_word in ["nice", "clean"]:
                        custom_title = "🎯 PURE PERFECTION"

                    visual_cards.append({
                        "type": pattern["card_type"],
                        "title": custom_title,
                        "keyword": clean_word.upper(),
                        "theme": pattern["theme"],
                        "start": start_time,
                        "end": min(start_time + card_dur, total_duration),
                        "duration": card_dur
                    })
                    last_card_end = start_time + card_dur

                    # Synchronize sound effect
                    sfx_cues.append({
                        "type": pattern["sfx"],
                        "time": start_time,
                        "volume": 0.75
                    })

                    # Micro punch-zoom on word impact
                    camera_moves.append({
                        "start": start_time,
                        "end": min(start_time + 0.6, total_duration),
                        "start_zoom": pattern.get("zoom", 1.10),
                        "end_zoom": 1.04,
                        "type": "PUNCH_CUT"
                    })
                break

    # Rhythmic retention keeper: if gap between cards > 5s, insert engagement booster
    if total_duration > 8.0:
        step = 0.0
        while step < total_duration - 3.0:
            # Check if any card is active during [step, step + 2.5]
            overlapping = any(c["start"] <= step + 2.5 and c["end"] >= step for c in visual_cards)
            if not overlapping and step >= 3.0:
                visual_cards.append({
                    "type": "ALERT_BADGE",
                    "title": "⚡ HIGH VOLTAGE REACTION",
                    "keyword": "IShowSpeed".upper(),
                    "theme": "warning",
                    "start": step,
                    "end": min(step + 2.0, total_duration),
                    "duration": 2.0
                })
                sfx_cues.append({"type": "pop", "time": step, "volume": 0.65})
                step += 4.5
            else:
                step += 2.0

        # Sort visual cards by start time
        visual_cards.sort(key=lambda x: x["start"])

    # Add loop cue at the end if video duration > 10s
    if total_duration > 10:
        sfx_cues.append({
            "type": "whoosh",
            "time": max(0.0, total_duration - 1.2),
            "volume": 0.65
        })

    return visual_cards, sfx_cues, camera_moves, broll_cues
