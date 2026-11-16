"""
generate_algorithm_short.py
Generates a complete, viral 9:16 YouTube Short explaining the 2026 YouTube Algorithm Jails:
  - 4-Beat P.A.V. Spine Hook (0-3s tension, no fluff)
  - Neural Voiceover via edge-tts
  - Faster-Whisper word-by-word active yellow karaoke subtitles
  - Background GTA gameplay footage from stream_IShowSpeed.ts
  - Ambient GTA theme BGM ducked under speech
  - Pre-upload Virality Test audit
"""

import os
import sys
import asyncio
import subprocess
import edge_tts
from faster_whisper import WhisperModel
import random
from virality_engine import ViralityTester, generate_spicy_seo

def select_gta_bgm() -> str | None:
    folder = "gta_tracks"
    if os.path.exists(folder):
        tracks = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith((".mp3", ".wav"))]
        if tracks:
            return random.choice(tracks)
    return None

FFMPEG = os.path.abspath("ffmpeg.exe") if os.path.exists("ffmpeg.exe") else "ffmpeg"
FFPROBE = os.path.abspath("ffprobe.exe") if os.path.exists("ffprobe.exe") else "ffprobe"

VOICEOVER_TEXT = (
    "Stop deleting your YouTube Shorts! You are not shadowbanned, you are trapped in YouTube's view jails. "
    "The 200 view jail happens when thirty percent of people swipe away in the first two seconds. If they swipe, YouTube kills your impressions. "
    "The 1K jail happens when your video has dead pauses and weak pacing. "
    "To escape: cut every silence over half a second, hook them in frame one, and loop your ending right back into the start. "
    "Which view jail are you stuck in right now?"
)

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

import win32com.client

def generate_speech_sync(text: str, output_wav: str):
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    temp_wav = "temp_sapi.wav"
    stream.Open(temp_wav, 3, False)
    speaker.AudioOutputStream = stream
    speaker.Rate = 2  # high energy, fast pacing
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

def generate_karaoke_ass(words: list, ass_path: str):
    header = """[Script Info]
Title: Algorithm Jails Explainer
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralActive,Montserrat Black,72,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,420,1
Style: ViralNormal,Montserrat Black,72,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    chunk_size = 4
    events = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if not chunk:
            continue
        c_start = chunk[0].start
        c_end = chunk[-1].end
        for active_idx, w in enumerate(chunk):
            w_start = format_ass_time(w.start)
            w_end = format_ass_time(w.end)
            formatted_words = []
            for j, other_w in enumerate(chunk):
                cleaned = other_w.word.strip().upper()
                if j == active_idx:
                    formatted_words.append(r"{\c&H0000FFFF\b1}" + cleaned + r"{\r}")
                else:
                    formatted_words.append(r"{\c&H00FFFFFF\b1}" + cleaned + r"{\r}")
            line_text = " ".join(formatted_words)
            events.append(f"Dialogue: 0,{w_start},{w_end},ViralNormal,,0,0,0,,{line_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

def main():
    print("=" * 65)
    print("  🎬  AI Video Generator: 2026 Algorithm Jails Explainer Short")
    print("=" * 65)

    os.makedirs("clips", exist_ok=True)
    voice_wav = "clips/algorithm_voiceover.wav"
    ass_path = "clips/algorithm_subtitles.ass"
    output_mp4 = "clips/escape_view_jails_2026_short.mp4"

    # Step 1: Synthesize voiceover
    print("[1/5] Synthesizing high-retention narration via Windows SAPI Engine...")
    generate_speech_sync(VOICEOVER_TEXT, voice_wav)
    
    import wave
    with wave.open(voice_wav, "r") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    print(f"[✔] Voiceover synthesized: {duration:.1f}s ({len(VOICEOVER_TEXT.split())} words)")

    # Step 2: Transcribe with Whisper for word sync
    print("[2/5] Aligning word-level timestamps with Faster-Whisper...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(voice_wav, word_timestamps=True)
    all_words = []
    for s in segments:
        for w in s.words:
            all_words.append(w)
    print(f"[✔] Aligned {len(all_words)} words")

    # Step 3: Generate ASS Subtitles
    print("[3/5] Generating Montserrat Black active-yellow karaoke subtitles...")
    generate_karaoke_ass(all_words, ass_path)

    # Step 4: Background gameplay video
    source_video = "stream_IShowSpeed.ts"
    if not os.path.exists(source_video):
        print(f"[!] Source video {source_video} not found!")
        return

    # Step 5: Render final composite with GTA BGM & Subtitles
    bgm_track = select_gta_bgm()
    print(f"[4/5] Selected GTA BGM: '{os.path.basename(bgm_track) if bgm_track else 'None'}'")
    print("[5/5] Rendering 9:16 vertical Short with FFmpeg...")

    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    
    # Video filter: Background blur + Foreground crisp zoom + Badge + Subtitles
    vf = (
        f"[0:v]trim=start=60:duration={duration},setpts=PTS-STARTPTS,"
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:3,eq=brightness=-0.15:saturation=1.2[bg];"
        f"[0:v]trim=start=60:duration={duration},setpts=PTS-STARTPTS,"
        f"scale=1080:-1,eq=contrast=1.06:brightness=0.02:saturation=1.12[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
        f"[base]drawtext=text='ALGORITHM INTEL 2026':fontcolor=white:fontsize=36:box=1:boxcolor=red@0.85:boxborderw=12:x=(w-text_w)/2:y=180,"
        f"ass=filename='{escaped_ass}'[vout]"
    )

    # Audio filter: Voiceover (100%) + BGM (8% volume, ducked)
    inputs = ["-i", source_video, "-i", voice_wav]
    if bgm_track and os.path.exists(bgm_track):
        inputs.extend(["-i", bgm_track])
        af = (
            f"[1:a]volume=1.0,aresample=48000[vocal];"
            f"[2:a]volume=0.08,aloop=loop=-1:size=2e+09,atrim=0:{duration},aresample=48000[bgm];"
            f"[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
    else:
        af = "[1:a]volume=1.0,aresample=48000[aout]"

    render_cmd = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", f"{vf};{af}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        output_mp4
    ]

    subprocess.run(render_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"\n[🎉 SUCCESS] Rendered Viral Short: {output_mp4} ({os.path.getsize(output_mp4) // (1024*1024)} MB)")

    # Virality Audit
    print("\n" + "=" * 50)
    print("  📊  RUNNING PRE-UPLOAD VIRALITY TEST GATE")
    print("=" * 50)
    word_dicts = [{"word": w.word, "start": w.start, "end": w.end} for w in all_words]
    title = "Why Your YouTube Shorts Are Stuck At 200 Views"
    audit = ViralityTester.audit_clip(
        video_path=output_mp4,
        transcript_words=word_dicts,
        title=title,
        ffmpeg_bin=FFMPEG
    )
    print(f"Audit Score: {audit['score']}/10.0 | Passed: {audit['passed']} (Threshold: {audit['threshold']})")
    for check_name, check_data in audit.get("checks", {}).items():
        print(f"  • {check_name}: {check_data}")

if __name__ == "__main__":
    main()
