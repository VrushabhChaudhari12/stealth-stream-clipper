"""
hypercraft/shotcraft_engine.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Video Shotcraft cinematography engine.
Transforms video into cinematic, high-retention 9:16 Shorts
using contextual entity visual popups (like https://www.youtube.com/shorts/L9IGhWkwpgo),
beat-transient cuts, and multi-layer FFmpeg compositing.
"""

import os
import subprocess
from hypercraft.motion_crafter import render_kinetic_hud_card, render_retention_graph_overlay, ASSETS_DIR
from hypercraft.sound_designer import build_sfx_track
from hypercraft.splitscreen_engine import SplitScreenEngine

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
FFMPEG = os.path.join(ROOT_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(ROOT_DIR, "ffmpeg.exe")) else "ffmpeg"


def build_shotcraft_filter_graph(
    source_video: str,
    duration: float,
    visual_cards: list[dict],
    ass_path: str,
    output_mp4: str,
    dialogue_wav: str,
    sfx_wav: str | None = None,
    bgm_track: str | None = None,
    bgm_volume: float = 0.08,
    broll_cues: list[dict] | None = None,
    start_sec: float = 0.0,
    layout_mode: str = "auto"
) -> bool:
    """
    Renders the complete cinematic composition using multi-layer FFmpeg filter graphs:
      - Layout: auto, cinematic (9:16 push-in), or reaction_split (top facecam + bottom game)
      - Layer Context: Contextual Entity Badges (Donald Mustard, Ronaldo, Young Speed)
      - Layer Top: 1-2 word centered high-impact karaoke subtitles
      - Audio: Dialogue (100%) + Procedural SFX (80%) + Auto-Ducked BGM (8%)
    """
    # 1. Render or load all visual card PNGs
    rendered_cards = []
    for i, card in enumerate(visual_cards):
        # If card already has an entity image path from asset_searcher
        if card.get("image_path") and os.path.exists(card["image_path"]):
            rendered_cards.append((card["image_path"], card["start"], card["end"]))
        elif card.get("type") == "SWIPE_INDICATOR":
            card_png = os.path.join(ASSETS_DIR, f"card_{i}.png")
            render_retention_graph_overlay(card_png)
            rendered_cards.append((card_png, card["start"], card["end"]))
        else:
            card_png = os.path.join(ASSETS_DIR, f"card_{i}.png")
            render_kinetic_hud_card(card, card_png)
            rendered_cards.append((card_png, card["start"], card["end"]))

    # 2. Build Video Filter Graph
    inputs = ["-i", source_video]
    vf_parts = []

    use_split = False
    if layout_mode == "reaction_split":
        use_split = True
    elif layout_mode == "auto":
        # Check if video has corner facecam
        se = SplitScreenEngine()
        samples = se.face_tracker.sample_video_faces(source_video, num_samples=10)
        face = se.face_tracker.find_reactor_face(1920, 1080, samples)
        if face is not None:
            use_split = True

    if use_split:
        se = SplitScreenEngine()
        split_res = se.build_reaction_split_filter(source_video)
        vf_parts.append(split_res["filter_graph"] + ";")
        curr_v = split_res["output_label"]
    else:
        # Base background: blurred, darkened, 60fps
        vf_parts.append(
            f"[0:v]trim=start={start_sec}:duration={duration},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:3,eq=brightness=-0.14:saturation=1.2[bg];"
        )
        # Foreground: smooth cinematic push-in zoom (0-3s) + continuous breathing drift
        vf_parts.append(
            f"[0:v]trim=start={start_sec}:duration={duration},setpts=PTS-STARTPTS,"
            f"zoompan=z='if(lte(it,2.5),1.0+0.14*(it/2.5),1.14)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=60,"
            f"scale=1080:-1,eq=contrast=1.06:brightness=0.02:saturation=1.12[fg];"
        )
        vf_parts.append(f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base0];")
        curr_v = "[base0]"

    input_idx = 1

    # Overlay B-roll cutaway video clips
    if broll_cues:
        for j, broll in enumerate(broll_cues):
            b_path = broll.get("path")
            if b_path and os.path.exists(b_path):
                inputs.extend(["-i", b_path])
                b_start = broll["start"]
                b_end = broll["end"]
                b_scaled = f"[broll_scale_{j}]"
                vf_parts.append(
                    f"[{input_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setpts=PTS-STARTPTS+{b_start}/TB{b_scaled};"
                )
                next_v = f"[base_broll_{j}]"
                vf_parts.append(f"{curr_v}{b_scaled}overlay=0:0:enable='between(t,{b_start:.2f},{b_end:.2f})'{next_v};")
                curr_v = next_v
                input_idx += 1

    # Overlay contextual entity badges at exact word timestamps
    for i, (card_png, start_t, end_t) in enumerate(rendered_cards):
        inputs.extend(["-i", card_png])
        next_v = f"[base_card_{i+1}]"
        fade_expr = f"enable='between(t,{start_t:.2f},{end_t:.2f})'"
        vf_parts.append(f"{curr_v}[{input_idx}:v]overlay=0:0:{fade_expr}{next_v};")
        curr_v = next_v
        input_idx += 1

    # Burn karaoke subtitles on top
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    vf_parts.append(f"{curr_v}ass=filename='{escaped_ass}'[vout]")

    # 3. Build Audio Filter Graph
    # Dialogue input
    inputs.extend(["-i", dialogue_wav])
    dialogue_idx = input_idx
    input_idx += 1

    audio_parts = [f"[{dialogue_idx}:a]volume=1.0,aresample=48000[vocal];"]
    mix_sources = ["[vocal]"]

    # SFX input
    if sfx_wav and os.path.exists(sfx_wav):
        inputs.extend(["-i", sfx_wav])
        sfx_idx = input_idx
        input_idx += 1
        audio_parts.append(f"[{sfx_idx}:a]volume=0.85,aresample=48000[sfx];")
        mix_sources.append("[sfx]")

    # BGM input
    if bgm_track and os.path.exists(bgm_track):
        inputs.extend(["-i", bgm_track])
        bgm_idx = input_idx
        input_idx += 1
        audio_parts.append(
            f"[{bgm_idx}:a]volume={bgm_volume},aloop=loop=-1:size=2e+09,atrim=0:{duration},aresample=48000[bgm];"
        )
        mix_sources.append("[bgm]")

    # Mix audio
    mix_count = len(mix_sources)
    all_audio = "".join(mix_sources)
    audio_parts.append(f"{all_audio}amix=inputs={mix_count}:duration=first:dropout_transition=2[aout]")

    full_filter = "".join(vf_parts) + ";" + "".join(audio_parts)

    cmd = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        output_mp4
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0
