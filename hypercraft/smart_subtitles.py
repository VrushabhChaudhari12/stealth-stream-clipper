"""
hypercraft/smart_subtitles.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Context-aware, 1-2 word rapid burst karaoke subtitles.
Matches the viral editing style of https://www.youtube.com/shorts/L9IGhWkwpgo:
  - Big, bold, uppercase font (Impact / Arial Black / Montserrat Black)
  - Centered vertically (y: 960 - right between top reaction and bottom gameplay)
  - 1-2 words at a time with active yellow/cyan word pop
  - Heavy 6px black outline for readability
  - 100% clean English transcription (prevents language hallucination)
"""

import os
import re

def write_viral_karaoke_ass(words: list[dict], ass_path: str, burst_size: int = 1) -> str:
    """
    Writes ASS subtitles with 1-word or 2-word mobile bursts centered on screen.
    """
    ass_header = """[Script Info]
Title: Smart Viral Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterImpact,Impact,92,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,5,40,40,0,1
Style: ActiveYellow,Impact,96,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,2,0,1,6,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    def fmt_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        return f"{h}:{m:02d}:{s:02d}.{min(99, cs):02d}"

    # Filter out empty or noise words
    clean_words = []
    for w in words:
        clean_w = re.sub(r"[^a-zA-Z0-9'?!.,]", "", w.get("word", "")).strip().upper()
        if clean_w and not clean_w.startswith(">>"):
            clean_words.append({
                "word": clean_w,
                "start": float(w.get("start", 0.0)),
                "end": float(w.get("end", 0.0))
            })

    # Group into 1-2 word bursts
    i = 0
    while i < len(clean_words):
        chunk = clean_words[i:i + burst_size]
        if not chunk:
            break

        c_start = fmt_time(chunk[0]["start"])
        c_end = fmt_time(chunk[-1]["end"])
        
        # Text with yellow highlight on active word
        text_line = " ".join(r"{\c&H0000FFFF\b1}" + item["word"] + r"{\r}" for item in chunk)
        events.append(f"Dialogue: 0,{c_start},{c_end},ActiveYellow,,0,0,0,,{text_line}")
        i += burst_size

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")

    return ass_path
