"""
hypercraft/swarm_orchestrator.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hermes-inspired autonomous multi-agent swarm orchestrator.
Coordinates specialized agents across Scout, Director, Motion Crafter,
Sound Engineer, and Virality Auditor to create benchmark viral videos.
"""

import os
import sys
import json
from faster_whisper import WhisperModel

from hypercraft.word_anchor import anchor_words_to_events
from hypercraft.sound_designer import build_sfx_track
from hypercraft.shotcraft_engine import build_shotcraft_filter_graph
from virality_engine import ViralityTester, score_emotion_context, SPICY_18_TITLES, SPICY_THUMB_HOOKS

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)


class SwarmOrchestrator:
    def __init__(self, whisper_model: str = "base"):
        print("\n" + "━" * 65)
        print("  ⚡  HYPERCRAFT SWARM ORCHESTRATOR v5.0 (HERMES-STYLE SWARM)")
        print("  👥  Active Agents: [Scout, Director, MotionCrafter, SoundEngineer, Auditor]")
        print("━" * 65)
        self.whisper = WhisperModel(whisper_model, device="cpu", compute_type="int8")

    def run_pipeline(
        self,
        source_video: str,
        dialogue_wav: str,
        duration: float,
        output_mp4: str,
        bgm_track: str | None = None,
        title: str = "Viral Clip #Shorts",
        target_streamer: str = "IShowSpeed",
        start_sec: float = 0.0
    ) -> dict:
        """
        Executes the autonomous 5-agent swarm pipeline:
          1. Scout & Director: Audio transcription and word-anchor event extraction
          2. MotionCrafter: Generates HUD glassmorphism cards and retention graphs
          3. SoundEngineer: Synthesizes whooshes, pops, bass drops, and auto-ducks music
          4. Shotcrafter: Assembles multi-layer FFmpeg composition
          5. ViralityAuditor: Evaluates clip against strict 8.5/10 retention gate
        """
        # Step 1: Director Agent - Transcribe and extract word timestamps
        print("\n[🤖 Director Agent] Aligning speech cadences and word timestamps...")
        segments, _ = self.whisper.transcribe(dialogue_wav, word_timestamps=True)
        all_words = []
        for s in segments:
            for w in s.words:
                all_words.append({"word": w.word, "start": w.start, "end": w.end})
        print(f"[✔] Aligned {len(all_words)} words across {duration:.1f}s")

        # Step 2: Word Anchor Agent - Bind kinetic events & SFX cues
        print("[🤖 WordAnchor Agent] Binding kinetic HUD cards, B-roll cutaways & SFX cues to spoken words...")
        visual_cards, sfx_cues, camera_moves, broll_cues = anchor_words_to_events(all_words, duration)
        print(f"[✔] Scheduled {len(visual_cards)} kinetic HUD cards, {len(broll_cues)} B-roll cutaways & {len(sfx_cues)} SFX cues")

        # Step 3: Sound Engineer Agent - Assemble procedural SFX track
        print("[🤖 SoundEngineer Agent] Building synchronized SFX track (whooshes, pops, bass hits)...")
        sfx_wav = os.path.join(ROOT_DIR, "clips", "hypercraft_sfx.wav")
        build_sfx_track(sfx_cues, duration, sfx_wav)
        print(f"[✔] Master SFX track compiled: {os.path.basename(sfx_wav)}")

        # Step 4: Motion Crafter Agent - Generate ASS karaoke subtitles
        print("[🤖 MotionCrafter Agent] Generating Montserrat Black active-yellow karaoke subtitles...")
        ass_path = os.path.join(ROOT_DIR, "clips", "hypercraft_subtitles.ass")
        self._write_ass_karaoke(all_words, ass_path, target_streamer)

        # Step 5: Shotcraft Render Engine
        print("[🤖 Shotcraft Engine] Executing multi-layer compositing (FG push-in + HUD cards + SFX + BGM)...")
        success = build_shotcraft_filter_graph(
            source_video=source_video,
            duration=duration,
            visual_cards=visual_cards,
            ass_path=ass_path,
            output_mp4=output_mp4,
            dialogue_wav=dialogue_wav,
            sfx_wav=sfx_wav,
            bgm_track=bgm_track,
            bgm_volume=0.08,
            broll_cues=broll_cues,
            start_sec=start_sec
        )

        if not success or not os.path.exists(output_mp4):
            return {"success": False, "error": "FFmpeg composition failed"}

        # Step 6: Virality Auditor Agent
        print("\n[🤖 Virality Auditor Agent] Auditing output against 2026 viral benchmark...")
        audit = ViralityTester.audit_clip(
            video_path=output_mp4,
            transcript_words=all_words,
            title=title,
            ffmpeg_bin=os.path.join(ROOT_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(ROOT_DIR, "ffmpeg.exe")) else "ffmpeg"
        )
        print(f"📊 HyperCraft Score: {audit['score']}/10.0 | Gate Passed: {audit['passed']}")
        for check, detail in audit.get("checks", {}).items():
            print(f"  • {check}: {detail}")

        return {
            "success": True,
            "output_mp4": output_mp4,
            "duration": duration,
            "audit": audit,
            "cards_count": len(visual_cards),
            "broll_count": len(broll_cues),
            "sfx_count": len(sfx_cues)
        }

    def _write_ass_karaoke(self, words: list[dict], ass_path: str, streamer: str):
        header = f"""[Script Info]
Title: HyperCraft Cinematic Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ActiveYellow,Montserrat Black,74,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,380,1
Style: InactiveWhite,Montserrat Black,74,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        chunk_size = 4
        events = []

        def fmt_time(sec: float) -> str:
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            cs = int(round((sec - int(sec)) * 100))
            return f"{h}:{m:02d}:{s:02d}.{min(99, cs):02d}"

        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            if not chunk:
                continue
            for active_idx, w in enumerate(chunk):
                w_start = fmt_time(w["start"])
                w_end = fmt_time(w["end"])
                formatted = []
                for j, other_w in enumerate(chunk):
                    raw_w = other_w["word"].strip().upper()
                    if j == active_idx:
                        formatted.append(r"{\c&H0000FFFF\b1}" + raw_w + r"{\r}")
                    else:
                        formatted.append(r"{\c&H00FFFFFF\b1}" + raw_w + r"{\r}")
                events.append(f"Dialogue: 0,{w_start},{w_end},InactiveWhite,,0,0,0,,{' '.join(formatted)}")

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")
