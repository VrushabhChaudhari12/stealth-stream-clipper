"""
super_clipper.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HyperCraft Super-Clipper v5.0 (Sovereign Swarm Edition)
Fuses Video Shotcraft, HyperFrames declarative motion graphics,
Hypit word-anchored events, and Hermes multi-agent swarm architecture.
"""

import os
import sys
import argparse
import random
import wave
import subprocess

from hypercraft.swarm_orchestrator import SwarmOrchestrator
from virality_engine import generate_spicy_seo

DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.path.join(DIR, "ffmpeg.exe") if os.path.exists(os.path.join(DIR, "ffmpeg.exe")) else "ffmpeg"


def select_bgm():
    folder = os.path.join(DIR, "gta_tracks")
    if os.path.exists(folder):
        tracks = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith((".mp3", ".wav"))]
        if tracks:
            return random.choice(tracks)
    return None


def generate_explainer_audio(text: str, output_wav: str):
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    temp_wav = os.path.join(DIR, "temp_sapi.wav")
    stream.Open(temp_wav, 3, False)
    speaker.AudioOutputStream = stream
    speaker.Rate = 2  # High-energy, fast conversational pace
    speaker.Speak(text)
    stream.Close()

    # Convert to 16kHz mono WAV for Whisper
    cmd = [
        FFMPEG, "-y", "-i", temp_wav,
        "-ar", "16000", "-ac", "1", output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(temp_wav):
        os.remove(temp_wav)


def main():
    parser = argparse.ArgumentParser(description="HyperCraft Super-Clipper v5.0")
    parser.add_argument("--mode", choices=["explainer", "vod", "live"], default="explainer",
                        help="Mode of operation: explainer video, vod slicing, or live stream monitoring")
    parser.add_argument("--source", default="stream_IShowSpeed.ts", help="Source video footage")
    parser.add_argument("--duration", type=float, default=26.0, help="Duration of clip in seconds")
    parser.add_argument("--title", default="Why Your Shorts Get Stuck at 200 Views", help="Video Title")
    parser.add_argument("--auto-upload", action="store_true", help="Auto-upload to YouTube if virality gate passes")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])

    args = parser.parse_args()

    os.makedirs(os.path.join(DIR, "clips"), exist_ok=True)
    orchestrator = SwarmOrchestrator(whisper_model="base")

    source_video = os.path.abspath(args.source)
    if not os.path.exists(source_video):
        print(f"[!] Source video {source_video} not found!")
        sys.exit(1)

    output_mp4 = os.path.join(DIR, "clips", "hypercraft_cinematic_short.mp4")
    dialogue_wav = os.path.join(DIR, "clips", "hypercraft_dialogue.wav")

    if args.mode == "explainer":
        explainer_script = (
            "Stop deleting your YouTube Shorts! You are not shadowbanned, you are trapped in YouTube's view jails. "
            "The 200 view jail happens when thirty percent of people swipe away in the first two seconds. If they swipe, YouTube kills your impressions. "
            "The 1K jail happens when your video has dead pauses and weak pacing. "
            "To escape: cut every silence over half a second, hook them in frame one, and loop your ending right back into the start. "
            "Which view jail are you stuck in right now?"
        )
        print(f"[*] Synthesizing script for explainer short...")
        generate_explainer_audio(explainer_script, dialogue_wav)

        with wave.open(dialogue_wav, "r") as wf:
            real_duration = wf.getnframes() / float(wf.getframerate())
    else:
        # VOD mode: extract audio from source video
        real_duration = args.duration
        cmd = [
            FFMPEG, "-y", "-ss", "30", "-i", source_video,
            "-t", str(real_duration), "-ar", "16000", "-ac", "1", dialogue_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    bgm_track = select_bgm()
    print(f"[*] Selected Soundtrack: {os.path.basename(bgm_track) if bgm_track else 'None'}")

    # Run the full autonomous swarm
    result = orchestrator.run_pipeline(
        source_video=source_video,
        dialogue_wav=dialogue_wav,
        duration=real_duration,
        output_mp4=output_mp4,
        bgm_track=bgm_track,
        title=args.title,
        target_streamer="IShowSpeed"
    )

    if result.get("success"):
        print("\n" + "=" * 65)
        print("  🎉  HYPERCRAFT CINEMATIC SHORT RENDERED SUCCESSFULLY!")
        print("=" * 65)
        print(f"Output File:     {output_mp4}")
        print(f"Duration:        {real_duration:.1f}s")
        print(f"Kinetic Cards:   {result['cards_count']}")
        print(f"B-Roll Cutaways: {result.get('broll_count', 0)}")
        print(f"Sound FX Cues:   {result['sfx_count']}")
        print(f"Virality Score:  {result['audit']['score']}/10.0 (Passed: {result['audit']['passed']})")
        print("=" * 65)

        if args.auto_upload and result['audit']['passed']:
            print("\n[*] Initiating YouTube Auto-Upload...")
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader()
            if uploader.authenticate():
                uploader.upload_short(
                    video_path=output_mp4,
                    title=f"{args.title} 🚨 #Shorts",
                    description=(
                        f"{args.title}\n\n"
                        "⚠️ Rated 18% Spicy | Unfiltered creator truth & harsh algorithm realities. Viewer discretion advised.\n\n"
                        "#Shorts #YouTubeAlgorithm #CreatorTips #AlgorithmHacks #Gaming"
                    ),
                    tags=["shorts", "youtube algorithm", "creator tips", "gaming"],
                    privacy_status=args.privacy,
                    category_id="27"
                )
    else:
        print(f"[!] Pipeline failed: {result.get('error')}")


if __name__ == "__main__":
    main()
