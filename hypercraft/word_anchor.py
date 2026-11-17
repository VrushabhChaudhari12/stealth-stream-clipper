"""
hypercraft/word_anchor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hypit-inspired word-level event anchoring.
Scans Whisper word timestamps to bind kinetic visual HUD cards,
shot cuts, and sound effect triggers directly to spoken words.
"""

import re

TRIGGER_PATTERNS = [
    # Danger / Negative Hook triggers
    {
        "keywords": ["stop", "deleting", "never", "wrong", "mistake", "shadowbanned", "trapped", "jail"],
        "card_type": "ALERT_BADGE",
        "title": "⚠️ CRITICAL MISTAKE",
        "theme": "danger",
        "sfx": "bass_hit",
        "zoom": 1.14
    },
    # Metric / Data triggers
    {
        "keywords": ["200", "1k", "1000", "zero", "percent", "thirty", "half"],
        "card_type": "DATA_METRIC",
        "title": "📊 ALGORITHM BENCHMARK",
        "theme": "metric",
        "sfx": "pop",
        "zoom": 1.08
    },
    # Motion / Action triggers
    {
        "keywords": ["swipe", "away", "kills", "scroll", "drop", "dead"],
        "card_type": "SWIPE_INDICATOR",
        "title": "📉 30% RETENTION WALL",
        "theme": "warning",
        "sfx": "whoosh",
        "zoom": 1.12
    },
    # Payoff / Solution triggers
    {
        "keywords": ["escape", "fix", "secret", "hack", "loop", "solution", "scale"],
        "card_type": "UNLOCK_CARD",
        "title": "🔓 RETENTION UNLOCKED",
        "theme": "success",
        "sfx": "alert",
        "zoom": 1.10
    }
]


def anchor_words_to_events(words: list[dict], total_duration: float) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Parses Whisper word timestamps.
    Returns:
      - visual_cards: list of kinetic HUD cards to render on screen
      - sfx_cues: list of audio sound effects synchronized to words
      - camera_moves: list of shot zoom/pan intervals
    """
    visual_cards = []
    sfx_cues = []
    camera_moves = []

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
    for w in words:
        clean_word = re.sub(r"[^a-zA-Z0-9%]", "", w.get("word", "").lower())
        start_time = float(w.get("start", 0.0))
        end_time = float(w.get("end", start_time + 0.3))

        for pattern in TRIGGER_PATTERNS:
            if clean_word in pattern["keywords"]:
                # Ensure minimum 1.8s spacing between cards so they don't overlap
                if start_time >= last_card_end + 0.5:
                    card_dur = 2.0
                    visual_cards.append({
                        "type": pattern["card_type"],
                        "title": pattern["title"],
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

    # Add loop cue at the end if video duration > 10s
    if total_duration > 10:
        sfx_cues.append({
            "type": "whoosh",
            "time": max(0.0, total_duration - 1.5),
            "volume": 0.6
        })

    return visual_cards, sfx_cues, camera_moves
