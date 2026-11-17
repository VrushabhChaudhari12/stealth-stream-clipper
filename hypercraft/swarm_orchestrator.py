"""
hypercraft/swarm_orchestrator.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Context-Aware Autonomous Multi-Agent Swarm Orchestrator.
Coordinates specialized agents across:
  - Director & Scout: Clean English speech transcription & sub-second word alignment
  - Context Analyzer: Semantic situation understanding & entity discovery
  - Asset Searcher: Automated web/Wikipedia reference image fetcher & circular badge generator
  - Sound Engineer: Synchronized 808 sub-bass drops & whooshes
  - Motion Crafter: 1-2 word rapid-burst Impact karaoke captions
  - Virality Auditor: 2026 Shorts algorithm benchmark evaluation
"""

import os
import sys
import json
import subprocess
from faster_whisper import WhisperModel

from hypercraft.context_analyzer import analyze_clip_context
from hypercraft.asset_searcher import search_entity_image
from hypercraft.smart_subtitles import write_viral_karaoke_ass
from hypercraft.sound_designer import build_sfx_track
from hypercraft.shotcraft_engine import build_shotcraft_filter_graph
from virality_engine import ViralityTester

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)


class SwarmOrchestrator:
    def __init__(self, whisper_model: str = "base"):
        print("\n" + "━" * 65)
        print("  ⚡  HYPERCRAFT SWARM ORCHESTRATOR v5.2 (CONTEXT-AWARE EDITION)")
        print("  👥  Active Agents: [Director, ContextAnalyzer, AssetSearcher, SoundEngineer, Auditor]")
        print("━" * 65)
        self.whisper = WhisperModel(whisper_model, device="cpu", compute_type="int8")

    def run_pipeline(
        self,
        source_video: str,
        dialogue_wav: str,
        duration: float,
        output_mp4: str,
        bgm_track: str | None = None,
        title: str | None = None,
        target_streamer: str = "Streamer",
        start_sec: float = 0.0,
        language: str = "en",
        layout_mode: str = "auto"
    ) -> dict:
        """
        Executes the context-aware editing pipeline:
          1. Transcribe speech with strict language enforcement (no broken transliteration)
          2. Understand clip situation, climax quote, and referenced entities
          3. Automatically search & craft floating circular entity badges (Donald Mustard, Ronaldo, etc.)
          4. Center-screen 1-2 word Impact karaoke subtitles
          5. Multi-layer compositing + auto-ducked soundtrack
          6. Virality benchmark audit
        """
        # Auto-extract dialogue WAV if missing
        if not os.path.exists(dialogue_wav):
            if not dialogue_wav.endswith(".wav"):
                dialogue_wav = os.path.splitext(source_video)[0] + "_extracted.wav"
            print(f"[🤖 Director Agent] Extracting dialogue audio to {dialogue_wav}...")
            ffmpeg_cmd = [
                os.path.join(ROOT_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(ROOT_DIR, "ffmpeg.exe")) else "ffmpeg",
                "-y", "-i", source_video, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", dialogue_wav
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Step 1: Director Agent - Transcribe cleanly
        print(f"\n[🤖 Director Agent] Transcribing dialogue with '{language}' language enforcement...")
        segments, _ = self.whisper.transcribe(dialogue_wav, word_timestamps=True, language=language, beam_size=3)
        all_words = []
        for s in segments:
            for w in s.words:
                all_words.append({"word": w.word, "start": w.start, "end": w.end})
        print(f"[✔] Aligned {len(all_words)} words across {duration:.1f}s")

        # Step 2: Context Analyzer Agent - Extract entities & situation
        print("[🤖 ContextAnalyzer Agent] Analyzing transcript context, punchlines & entities...")
        context = analyze_clip_context(all_words, duration)
        print(f"  • Climax Quote: \"{context['climax_quote']}\"")
        print(f"  • Entities Detected: {[e['entity'] for e in context['entities']]}")
        print(f"  • Context Title: {context['title']}")
        print(f"  • Thumbnail Hook: {context['thumb_hook']}")

        # Step 3: Asset Searcher Agent - Search & generate reference badges
        visual_cards = []
        sfx_cues = []
        
        # Opening camera hook
        sfx_cues.append({"type": "whoosh", "time": 0.05, "volume": 0.65})

        for ent in context["entities"]:
            print(f"[🤖 AssetSearcher Agent] Searching web reference image for '{ent['entity']}'...")
            badge_png = search_entity_image(ent["entity"])
            if badge_png and os.path.exists(badge_png):
                print(f"[✔] Generated circular reference badge: {os.path.basename(badge_png)}")
                visual_cards.append({
                    "type": "ENTITY_BADGE",
                    "image_path": badge_png,
                    "keyword": ent["keyword"],
                    "start": ent["start"],
                    "end": ent["end"]
                })
                sfx_cues.append({
                    "type": "pop",
                    "time": ent["start"],
                    "volume": 0.85
                })

        # Step 4: Sound Engineer Agent - Assemble procedural SFX track
        print("[🤖 SoundEngineer Agent] Building synchronized SFX track (whooshes, pops, bass hits)...")
        sfx_wav = os.path.join(ROOT_DIR, "clips", "hypercraft_sfx.wav")
        build_sfx_track(sfx_cues, duration, sfx_wav)

        # Step 5: Motion Crafter Agent - Generate centered 1-2 word Impact subtitles
        print("[🤖 MotionCrafter Agent] Generating centered 1-2 word Impact karaoke subtitles...")
        ass_path = os.path.join(ROOT_DIR, "clips", "hypercraft_subtitles.ass")
        write_viral_karaoke_ass(all_words, ass_path, burst_size=1)

        # Step 6: Shotcraft Render Engine
        print("[🤖 Shotcraft Engine] Executing multi-layer compositing (FG push-in + Entity Badges + SFX + BGM)...")
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
            start_sec=start_sec,
            layout_mode=layout_mode
        )

        if not success or not os.path.exists(output_mp4):
            return {"success": False, "error": "FFmpeg composition failed"}

        final_title = title if title else context["title"]

        # Step 7: Virality Auditor Agent & Master Quality Gate
        print("\n[🤖 Virality Auditor Agent] Auditing output against 2026 viral benchmark & Master Quality Gate...")
        audit = ViralityTester.audit_clip(
            video_path=output_mp4,
            transcript_words=all_words,
            title=final_title,
            ffmpeg_bin=os.path.join(ROOT_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(ROOT_DIR, "ffmpeg.exe")) else "ffmpeg"
        )
        print(f"📊 HyperCraft Score: {audit['score']}/10.0 | Gate Passed: {audit['passed']}")
        for check, detail in audit.get("checks", {}).items():
            print(f"  • {check}: {detail}")

        # Run 7-Stage Pre-Flight Quality Gate
        from virality_engine import MasterQualityGate
        mqg = MasterQualityGate()
        clip_meta = {
            "title": final_title,
            "duration": duration,
            "visual_cards": visual_cards,
            "sfx_count": len(sfx_cues),
            "thumb_hook": context.get("thumb_hook", "")
        }
        gate_res = mqg.evaluate_clip(clip_meta, all_words, video_path=output_mp4)
        print(f"\n🛡️ [Master Quality Gate] Score: {gate_res['total_score']:.1f}/100.0 | Verdict: {gate_res['verdict']}")
        print(f"  • Passing Threshold: {gate_res['threshold']}")
        if gate_res.get("gate_failures"):
            print(f"  • Gate Failures: {gate_res['gate_failures']}")
        for st_name, score in gate_res.get("score_breakdown", {}).items():
            print(f"    - {st_name}: {score} pts")

        return {
            "success": True,
            "output_mp4": output_mp4,
            "duration": duration,
            "context": context,
            "audit": audit,
            "gate_evaluation": gate_res,
            "cards_count": len(visual_cards),
            "sfx_count": len(sfx_cues),
            "title": final_title,
            "thumb_hook": context["thumb_hook"]
        }
