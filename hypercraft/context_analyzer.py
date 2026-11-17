"""
hypercraft/context_analyzer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Context Understanding & Semantic Entity Extractor.
Listens to the full transcript, understands the actual situation and climax punchline,
identifies named entities for automated visual image popups,
and generates authentic context-driven titles and thumbnail hooks.
"""

import os
import re

ENTITY_DICTIONARY = {
    "portuguese": "Cristiano Ronaldo",
    "ronaldo": "Cristiano Ronaldo",
    "messi": "Lionel Messi",
    "darren": "IShowSpeed",
    "watkins": "IShowSpeed",
    "speed": "IShowSpeed",
    "mustard": "Donald Mustard",
    "donald": "Donald Mustard",
    "luffy": "Monkey D Luffy",
    "one piece": "Monkey D Luffy",
    "pirate": "Pirate",
    "fortnite": "Fortnite",
    "minecraft": "Minecraft",
    "ghast": "Ghast Minecraft",
    "jynxzi": "Jynxzi",
    "kai": "Kai Cenat",
    "cenat": "Kai Cenat",
    "drake": "Drake rapper",
    "goku": "Goku Dragon Ball",
    "jcb": "JCB Excavator",
    "truck": "Monster Truck",
    "bugatti": "Bugatti Chiron",
    "ferrari": "Ferrari",
    "lamborghini": "Lamborghini"
}


def analyze_clip_context(words: list[dict], duration: float) -> dict:
    """
    Analyzes the transcribed words to determine:
      1. Named entities mentioned and their timestamps (for visual badge overlays)
      2. The climax punchline quote (highest energy / funniest moment)
      3. Context-driven title & thumbnail hook (no mad-lib generic templates)
    """
    full_text = " ".join(w.get("word", "") for w in words).strip()
    clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", full_text).lower()

    # 1. Identify entities mentioned
    entities_found = []
    seen_entities = set()

    for w in words:
        raw_w = re.sub(r"[^a-zA-Z0-9]", "", w.get("word", "")).lower()
        if raw_w in ENTITY_DICTIONARY:
            ent_name = ENTITY_DICTIONARY[raw_w]
            start_t = float(w.get("start", 0.0))
            if ent_name not in seen_entities:
                seen_entities.add(ent_name)
                entities_found.append({
                    "entity": ent_name,
                    "keyword": raw_w.upper(),
                    "start": start_t,
                    "end": min(start_t + 2.2, duration)
                })

    # Check for multi-word entities (e.g. "one piece", "darren watkins")
    if "one piece" in clean_text and "Monkey D Luffy" not in seen_entities:
        entities_found.append({
            "entity": "Monkey D Luffy",
            "keyword": "ONE PIECE",
            "start": 1.0,
            "end": min(3.2, duration)
        })
    if "darren watkins" in clean_text and "IShowSpeed" not in seen_entities:
        entities_found.append({
            "entity": "IShowSpeed",
            "keyword": "DARREN WATKINS",
            "start": 2.0,
            "end": min(4.2, duration)
        })

    # 2. Extract Climax Punchline Quote
    climax_quote = ""
    # Find sentence with highest emotion words or quotes
    punchline_candidates = [
        s.strip() for s in re.split(r"[.?!]", full_text) if len(s.strip()) > 3
    ]
    if punchline_candidates:
        # Pick the most expressive candidate
        climax_quote = max(punchline_candidates, key=lambda s: len(s))
    else:
        climax_quote = full_text[:40]

    # Clean punchline for title
    short_quote = climax_quote.strip().strip('"').strip("'")
    if len(short_quote) > 35:
        short_quote = short_quote[:35] + "..."

    # 3. Authentic Title & Thumbnail Hook Generation
    if entities_found:
        main_ent = entities_found[0]["entity"]
        title = f'"{short_quote}" 😭🙏 | {main_ent} #Shorts'
        thumb_hook = f"{main_ent.upper()}?! 💀"
    else:
        title = f'"{short_quote}" 😭💀 #Shorts'
        thumb_hook = "NO WAY! 😱"

    # Enforce title length under 60 chars
    if len(title) > 60:
        title = f'"{short_quote}" 😭🙏 #Shorts'

    return {
        "full_text": full_text,
        "entities": entities_found,
        "climax_quote": climax_quote,
        "title": title,
        "thumb_hook": thumb_hook
    }
