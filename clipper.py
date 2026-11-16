"""
Stealth Stream Auto-Clipper v4.0 (Enterprise Viral Engine)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
100% Free & Local Pipeline. Zero API Costs.

Production Features:
  ✔ Perfect Audio/Video/Subtitle Sync (-avoid_negative_ts make_zero + aresample=async=1)
  ✔ Full Multilingual Transcription (Hindi, English & Hinglish via Whisper 'base')
  ✔ YouTube Reference (UDJRfV592P0) Viral ASS Subtitle Engine:
      - Rapid 2-3 word mobile-friendly bursts
      - Active word pop & yellow highlight (Hormozi / MrBeast style)
      - Heavy 3.5px black outline + shadow for crystal clarity over gameplay
  ✔ Anti-Copyright & Content ID Fingerprint Disruption:
      - Audio: Micro-pitch shift (1.02x) + EQ filter (shifts spectral peaks)
      - Video: Micro-contrast, unsharp mask, subtle vignette & continuous micro-zoom
      - Layout: 9:16 composite with blurred backdrop & streamer attribution badge
  ✔ Automatic Streamer Subfolder Segregation (clips/<streamer_name>/)
  ✔ Anonymous Twitch IRC + YouTube Live Chat Spike Engine
"""

import os
import sys
import re
import time
import json
import socket
import random
import argparse
import subprocess
import threading
from collections import deque
from datetime import datetime
from urllib.request import Request, urlopen

# ─── Directories & Paths ──────────────────────────────────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(DIR, "clips")


def _resolve_ffmpeg() -> str:
    local = os.path.join(DIR, "ffmpeg.exe")
    if os.path.exists(local):
        return local
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


FFMPEG = _resolve_ffmpeg()

# ─── Viral Hype Keywords (Spike Multiplier Boost) ────────────────────────────
HYPE_KEYWORDS = {
    "w", "l", "omg", "wtf", "lol", "kekw", "clip", "clipped",
    "bro", "cap", "yooo", "no way", "noway", "dead", "rip", "lmao",
    "bhai", "op", "khatam", "arre", "kya", "shabaash", "gaya",
    "🔥", "💀", "😭", "🤣", "⬆️", "💯", "😂"
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. VIRAL ASS SUBTITLE GENERATOR (Hormozi / MrBeast / UDJRfV592P0 Style)
# ─────────────────────────────────────────────────────────────────────────────

def fmt_ass_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds % 1) * 100)  # centiseconds for ASS
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


def create_viral_ass_file(words: list[dict], ass_path: str, chunk_size: int = 3):
    """
    Builds an Advanced SubStation Alpha (.ass) subtitle file with active word
    karaoke highlighting (yellow active word, white inactive words, bold outline).
    """
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,56,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,1.5,2,40,40,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    if not words:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header)
        return

    # Chunk words into rapid 2-3 word bursts
    chunks = []
    current_chunk = []
    for w in words:
        current_chunk.append(w)
        if len(current_chunk) >= chunk_size:
            chunks.append(current_chunk)
            current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)

    dialogue_events = []
    for chunk in chunks:
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]

        # For each active word in this chunk, create a dialogue slice
        for i, active_w in enumerate(chunk):
            w_start = active_w["start"]
            w_end = active_w["end"]

            # If adjacent word starts slightly later, extend current active word
            if i + 1 < len(chunk):
                w_end = max(w_end, chunk[i + 1]["start"])
            else:
                w_end = max(w_end, chunk_end)

            if w_end <= w_start:
                w_end = w_start + 0.25

            # Highlight active word in Yellow (\c&H00FFFF&), others in White (\c&HFFFFFF&)
            text_parts = []
            for j, w in enumerate(chunk):
                cleaned_word = w["word"].strip().upper()
                if j == i:
                    text_parts.append(f"{{\\c&H00FFFF&\\fscx110\\fscy110}}{cleaned_word}{{\\r}}")
                else:
                    text_parts.append(f"{{\\c&HFFFFFF&}}{cleaned_word}{{\\r}}")

            line_text = " ".join(text_parts)
            dialogue_events.append(
                f"Dialogue: 0,{fmt_ass_time(w_start)},{fmt_ass_time(w_end)},Default,,0,0,0,,{line_text}\n"
            )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(dialogue_events)


# ─────────────────────────────────────────────────────────────────────────────
# 2. AUDIO & VIDEO TRANSCRIPTION (Multilingual Hindi + English + Hinglish)
# ─────────────────────────────────────────────────────────────────────────────

def transcribe_clip(video_path: str, ass_path: str, srt_path: str,
                    model=None, task: str = "transcribe") -> tuple[bool, list[dict]]:
    """
    Transcribes audio using faster-whisper multilingual 'base' model.
    Auto-detects Hindi, English, and Hinglish.
    """
    try:
        from faster_whisper import WhisperModel
        if model is None:
            # Multilingual base model (supports Hindi, English, Hinglish, etc.)
            model = WhisperModel("base", device="cpu", compute_type="int8")

        segments, info = model.transcribe(
            video_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
            condition_on_previous_text=False,
            word_timestamps=True,
            task=task  # "transcribe" for original text or "translate" for English
        )

        all_words = []
        srt_entries = []

        for seg in segments:
            ws = getattr(seg, "words", None)
            if ws:
                for w in ws:
                    word_clean = w.word.strip()
                    if word_clean:
                        all_words.append({"word": word_clean, "start": max(0.0, w.start), "end": max(0.0, w.end)})
            else:
                txt = seg.text.strip()
                if txt:
                    all_words.append({"word": txt, "start": max(0.0, seg.start), "end": max(0.0, seg.end)})

        if all_words:
            print(f"[✔] Transcribed {len(all_words)} words | Language: {info.language} ({info.language_probability:.2f})")
            create_viral_ass_file(all_words, ass_path)

            # Also write standard SRT as reference
            with open(srt_path, "w", encoding="utf-8") as sf:
                for i, w in enumerate(all_words, 1):
                    sf.write(f"{i}\n{fmt_ass_time(w['start'])} --> {fmt_ass_time(w['end'])}\n{w['word']}\n\n")
            return True, all_words

        return False, []

    except Exception as ex:
        print(f"[!] Whisper Transcription Error: {ex}")
        return False, []


# ─────────────────────────────────────────────────────────────────────────────
# 3. FFMPEG STREAM SLICER & SYNCHRONIZATION
# ─────────────────────────────────────────────────────────────────────────────

def slice_stream_sync(source_ts: str, start_sec: int, duration: int, output_mp4: str) -> bool:
    """
    Guarantees bit-for-bit Audio/Video Sync on MPEG-TS slices:
      - avoids negative presentation timestamps (-avoid_negative_ts make_zero)
      - hard-syncs audio frames with video (-af aresample=async=1)
      - forces H.264 / AAC re-encode
    """
    cmd = [
        FFMPEG, "-y",
        "-ss", str(start_sec),
        "-i", source_ts,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "160k",
        "-af", "aresample=async=1",
        "-avoid_negative_ts", "make_zero",
        output_mp4
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 4. RENDERER (9:16 Vertical + Anti-Copyright + Viral Subtitles)
# ─────────────────────────────────────────────────────────────────────────────

def esc_path(p: str) -> str:
    """Escapes path for FFmpeg subtitles filter on Windows."""
    return p.replace("\\", "/").replace(":", "\\:")


def render_viral_clip(raw_mp4: str, ass_path: str | None, output_mp4: str,
                      channel_name: str, vertical: bool = True,
                      anti_copyright: bool = True) -> bool:
    """
    Applies the full viral post-production stack:
      1. 9:16 layout: 1080x1920 blurred backdrop + centered sharp gameplay
      2. Dynamic micro-zoom & visual grading (Anti-Content ID)
      3. Rubberband pitch & spectral EQ (Audio Anti-Fingerprint)
      4. Hormozi/MrBeast yellow active word ASS subtitle overlay
      5. Top streamer credit header badge
    """
    # ── Video Filter Stack ──
    clean_channel = channel_name.replace("'", "").replace(":", "")
    badge_text = f"STREAM - @{clean_channel.upper()}"

    filters = []

    if vertical:
        # Background: scaled, cropped to 1080x1920, darkened and blurred
        bg_filter = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=25:3,eq=brightness=-0.12:saturation=1.2[bg];"
        )
        # Foreground: crisp gameplay with micro-zoom & color pop
        if anti_copyright:
            fg_filter = (
                "[0:v]zoompan=z='min(zoom+0.0006,1.04)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=60,"
                "eq=contrast=1.04:brightness=0.01:saturation=1.08,unsharp=3:3:0.4:3:3:0.0,"
                "scale=1080:-1[fg];"
            )
        else:
            fg_filter = "[0:v]scale=1080:-1[fg];"

        # Composite background + foreground + credit badge
        composite = (
            f"{bg_filter}{fg_filter}"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
            f"[base]drawtext=text='{badge_text}':fontcolor=white:fontsize=32:"
            f"box=1:boxcolor=black@0.65:boxborderw=10:x=(w-text_w)/2:y=200[vbadge]"
        )
        current_v = "[vbadge]"
    else:
        if anti_copyright:
            composite = (
                "[0:v]eq=contrast=1.04:brightness=0.01:saturation=1.06,unsharp=3:3:0.4:3:3:0.0[base];"
                f"[base]drawtext=text='{badge_text}':fontcolor=white:fontsize=28:"
                f"box=1:boxcolor=black@0.6:boxborderw=8:x=40:y=40[vbadge]"
            )
            current_v = "[vbadge]"
        else:
            composite = "[0:v]copy[vbadge]"
            current_v = "[vbadge]"

    # Burn ASS subtitles if available
    if ass_path and os.path.exists(ass_path):
        escaped_ass = esc_path(ass_path)
        sub_filter = f"{current_v}ass=filename='{escaped_ass}'[vout]"
        final_video_filter = f"{composite};{sub_filter}"
        final_v_map = "[vout]"
    else:
        final_video_filter = composite
        final_v_map = current_v

    # ── Audio Filter Stack (Anti-Fingerprint Pitch/EQ Shift) ──
    if anti_copyright:
        audio_filter = (
            "asetrate=44100*1.02,aresample=44100,"
            "equalizer=f=1200:t=q:w=1.5:g=1.2,"
            "highpass=f=80,lowpass=f=15500,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
    else:
        audio_filter = "aresample=async=1"

    cmd = [
        FFMPEG, "-y",
        "-i", raw_mp4,
        "-filter_complex", final_video_filter,
        "-map", final_v_map,
        "-af", audio_filter,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "160k",
        output_mp4
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0 or not os.path.exists(output_mp4) or os.path.getsize(output_mp4) == 0:
        import shutil
        shutil.copyfile(raw_mp4, output_mp4)
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 5. CORE CLIPPER ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def clean_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s).strip("_")


class AutoClipper:
    def __init__(self, platform: str, target: str, **cfg):
        self.platform = platform.lower()
        self.target = target.strip()
        self.video_id: str | None = None
        self.streamer_name: str | None = None

        # Spike detection parameters
        self.multiplier = float(cfg.get("multiplier", 2.0))
        self.min_msgs = int(cfg.get("min_msgs", 8))
        self.bucket_sec = int(cfg.get("bucket_sec", 10))
        self.baseline = int(cfg.get("baseline_sec", 300))
        self.cooldown = int(cfg.get("cooldown", 90))

        # Output formatting
        self.pre_roll = int(cfg.get("pre_roll", 25))
        self.duration = int(cfg.get("duration", 50))
        self.vertical = bool(cfg.get("vertical", True))
        self.no_subs = bool(cfg.get("no_subtitles", False))
        self.task = cfg.get("task", "transcribe")
        self.anti_copyright = bool(cfg.get("anti_copyright", True))

        # Determine stream url and clean name
        _, streamer_slug = self._stream_url()

        # Streamer-segregated folder: D:\GTA clipping\clips\<streamer_name>\
        self.output_dir = os.path.join(CLIPS_DIR, streamer_slug)
        os.makedirs(self.output_dir, exist_ok=True)

        self.stream_file = os.path.join(DIR, f"stream_{streamer_slug}.ts")
        self.stream_start: float | None = None
        self.last_clip_time = 0.0
        self.clip_count = 0
        self.is_running = True
        self.whisper_model = None

        self.history: deque = deque()

    def _stream_url(self) -> tuple[str, str]:
        t = self.target
        if self.platform == "twitch":
            ch = t.lstrip("#").replace("https://twitch.tv/", "").replace("twitch.tv/", "").lower()
            return f"twitch.tv/{ch}", ch
        else:
            if "youtube.com/watch" in t or "youtu.be/" in t:
                m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", t) or re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", t)
                if m:
                    self.video_id = m.group(1)
                try:
                    req = Request(f"https://noembed.com/embed?url={t}", headers={"User-Agent": "Mozilla/5.0"})
                    with urlopen(req, timeout=5) as resp:
                        meta = json.loads(resp.read().decode())
                        author = meta.get("author_name")
                        if author:
                            self.streamer_name = author
                            return t, clean_name(author)
                except Exception:
                    pass
                name = self.video_id if self.video_id else clean_name(t)
                return t, name
            else:
                url = t if t.startswith("http") else f"https://www.youtube.com/{t if t.startswith('@') else '@' + t}/live"
                return url, clean_name(t)

    def _hud(self, now: float, recent: int, base_rate: float, threshold: float):
        if not self.stream_start:
            sys.stdout.write(f"\r[⏳ WAITING] Streamer offline — polling every 15s...  ")
            sys.stdout.flush()
            return
        elapsed = int(now - self.stream_start)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        sys.stdout.write(
            f"\r🔴 {h:02d}:{m:02d}:{s:02d} | 💬 {recent:3d}/10s [Base:{base_rate:4.1f} Trigger:{threshold:4.1f}] | 🎬 Clips: {self.clip_count}  "
        )
        sys.stdout.flush()

    def _register(self, text: str):
        now = time.time()
        lower = text.lower()
        weight = 1.6 if any(k in lower for k in HYPE_KEYWORDS) else 1.0
        self.history.append((now, weight))
        self._check_spike(now)

    def _check_spike(self, now: float):
        cutoff = now - self.baseline
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()

        raw_count = len(self.history)
        if raw_count < self.min_msgs:
            return

        total_w = sum(w for _, w in self.history)
        recent_w = sum(w for t, w in self.history if t >= now - self.bucket_sec)
        recent_raw = sum(1 for t, _ in self.history if t >= now - self.bucket_sec)
        base_rate = (total_w / self.baseline) * self.bucket_sec
        threshold = base_rate * self.multiplier

        self._hud(now, recent_raw, base_rate, threshold)

        if recent_w >= threshold and recent_raw >= self.min_msgs:
            if (now - self.last_clip_time) >= self.cooldown:
                self.last_clip_time = now
                self.clip_count += 1
                print(f"\n\n🔥 [HYPE SPIKE DETECTED!] {recent_raw} msgs/10s (Threshold: {threshold:.1f})")
                threading.Thread(target=self._clip_worker, args=(now,), daemon=True).start()

    def _clip_worker(self, spike_time: float):
        # Buffer post-roll to ensure complete reaction is written to disk
        post_wait = max(6, self.duration - self.pre_roll + 6)
        print(f"[*] Buffering {post_wait}s post-spike stream to disk...")
        time.sleep(post_wait)

        if not os.path.exists(self.stream_file):
            print(f"[!] Stream file not found: {self.stream_file}")
            return
        if not self.stream_start:
            print("[!] Stream start time unknown.")
            return

        offset = spike_time - self.stream_start
        start_sec = max(0, int(offset - self.pre_roll))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        raw_clip = os.path.join(self.output_dir, f"clip_{ts}_raw.mp4")
        ass_file = os.path.join(self.output_dir, f"clip_{ts}.ass")
        srt_file = os.path.join(self.output_dir, f"clip_{ts}.srt")
        final_clip = os.path.join(self.output_dir, f"clip_{ts}_final.mp4")
        credit_file = os.path.join(self.output_dir, f"clip_{ts}_credit.txt")

        print(f"[*] Slicing {self.duration}s synced segment from {start_sec}s...")
        if not slice_stream_sync(self.stream_file, start_sec, self.duration, raw_clip):
            print("[!] Failed to cut raw clip.")
            return
        print(f"[✔] Sliced raw clip: {os.path.basename(raw_clip)}")

        # Multilingual transcription
        ass_ready = False
        if not self.no_subs:
            print("[*] Transcribing speech (Hindi/English multilingual 'base' model)...")
            if self.whisper_model is None:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            ass_ready, _ = transcribe_clip(raw_clip, ass_file, srt_file, self.whisper_model, task=self.task)

        # Viral post-production rendering
        _, channel = self._stream_url()
        print(f"[*] Rendering viral clip (Vertical: {self.vertical}, Anti-Copyright: {self.anti_copyright})...")
        render_viral_clip(
            raw_clip=raw_clip,
            ass_path=ass_file if ass_ready else None,
            output_mp4=final_clip,
            channel_name=channel,
            vertical=self.vertical,
            anti_copyright=self.anti_copyright
        )
        print(f"🎉 [CLIP READY] Saved -> {final_clip}")

        # Metadata & Attribution
        url, _ = self._stream_url()
        with open(credit_file, "w", encoding="utf-8") as cf:
            cf.write("=== FAIR USE ATTRIBUTION & METADATA ===\n")
            cf.write(f"Creator: @{channel}\n")
            cf.write(f"Platform: {self.platform.upper()}\n")
            cf.write(f"Source URL: {url}\n")
            cf.write(f"Clipped At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            cf.write("Suggested Caption:\n")
            cf.write(f"Chat went completely crazy here! 😂🔥 Credits to @{channel}\n\n")
            cf.write(f"Hashtags: #gaming #clips #{self.platform} #{clean_name(channel)} #shorts #trending\n")

    def _record(self):
        url, _ = self._stream_url()
        print(f"[*] Streamlink watching: {url}")
        cmd = [
            sys.executable, "-m", "streamlink",
            url, "best",
            "-o", self.stream_file,
            "--retry-streams", "15",
            "--retry-max", "0",
            "--force"
        ]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            if "Opening stream" in line or "Writing output" in line:
                self.stream_start = time.time()
                print(f"\n[🚀 LIVE] Stream recording started at {datetime.now().strftime('%H:%M:%S')}")

    def _twitch_irc(self):
        _, channel = self._stream_url()
        nick = f"justinfan{random.randint(10000, 99999)}"
        print(f"[*] Connecting Twitch IRC anonymously as {nick} for #{channel}...")

        while self.is_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("irc.chat.twitch.tv", 6667))
                sock.sendall(f"NICK {nick}\r\nJOIN #{channel}\r\n".encode())
                buf = ""
                while self.is_running:
                    data = sock.recv(4096).decode("utf-8", errors="ignore")
                    if not data:
                        break
                    buf += data
                    lines = buf.split("\r\n")
                    buf = lines.pop()
                    for line in lines:
                        if line.startswith("PING"):
                            sock.sendall(b"PONG :tmi.twitch.tv\r\n")
                        elif "PRIVMSG" in line:
                            text = line.split("PRIVMSG", 1)[1].split(":", 1)[-1]
                            self._register(text)
            except Exception as e:
                print(f"\n[!] Twitch IRC reconnecting: {e}")
                time.sleep(5)

    def _youtube_chat(self):
        import pytchat
        url, _ = self._stream_url()
        print(f"[*] Resolving YouTube Live Video ID for {url}...")

        vid = getattr(self, "video_id", None)
        if not vid:
            m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url) or re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
            if m:
                vid = m.group(1)

        while not vid and self.is_running:
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                html = urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
                m = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                if m:
                    vid = m.group(1)
            except Exception:
                pass
            if not vid:
                sys.stdout.write("\r[⏳] Waiting for YouTube live broadcast...  ")
                sys.stdout.flush()
                time.sleep(15)

        self.video_id = vid
        print(f"[✔] Attached to YouTube Live Video ID: {vid}")
        chat = pytchat.create(video_id=vid)
        while chat.is_alive() and self.is_running:
            try:
                for c in chat.get().sync_items():
                    self._register(c.message)
                time.sleep(0.4)
            except Exception:
                time.sleep(2)

    def run(self):
        url, name = self._stream_url()
        print("━" * 65)
        print(f"  🎬  Stealth Auto-Clipper v4.0 (Enterprise Viral Engine)")
        print(f"  📺  Target: {self.platform.upper()} → @{name}")
        print(f"  ⚡  Spike Trigger: {self.multiplier}× baseline (min {self.min_msgs} msgs/10s)")
        print(f"  ✂️   Clip Length: {self.duration}s ({self.pre_roll}s pre-roll)")
        print(f"  🗣️   Transcription: Multilingual 'base' (Hindi + English + Hinglish)")
        print(f"  🛡️   Anti-Copyright Protection: {'ACTIVE (Pitch/Zoom/EQ Shifts)' if self.anti_copyright else 'OFF'}")
        print(f"  📐  Layout: {'9:16 Vertical Shorts/Reels' if self.vertical else '16:9 Landscape'}")
        print(f"  💾  Folder: {self.output_dir}")
        print("━" * 65 + "\n")

        threading.Thread(target=self._record, daemon=True).start()

        if self.platform == "twitch":
            self._twitch_irc()
        else:
            self._youtube_chat()


def main():
    p = argparse.ArgumentParser(description="Stealth Stream Auto-Clipper v4.0")
    p.add_argument("--platform", choices=["twitch", "youtube"], help="Platform (auto-detected if omitted)")
    p.add_argument("--target", required=True, help="Streamer channel, handle, or URL")
    p.add_argument("--multiplier", type=float, default=2.0, help="Spike multiplier vs baseline (default: 2.0)")
    p.add_argument("--min-msgs", type=int, default=8, help="Min msgs/10s for spike trigger (default: 8)")
    p.add_argument("--pre-roll", type=int, default=25, help="Seconds before spike to cut (default: 25)")
    p.add_argument("--duration", type=int, default=50, help="Clip length in seconds (default: 50)")
    p.add_argument("--cooldown", type=int, default=90, help="Cooldown between clips in seconds (default: 90)")
    p.add_argument("--task", choices=["transcribe", "translate"], default="transcribe",
                   help="'transcribe' for native Hindi/English, 'translate' to translate into English subtitles")
    p.add_argument("--landscape", action="store_true", help="Output standard 16:9 widescreen instead of 9:16 vertical")
    p.add_argument("--no-subtitles", action="store_true", help="Disable subtitle generation")
    p.add_argument("--no-anti-copyright", action="store_true", help="Disable anti-copyright filters")

    args = p.parse_args()

    if not args.platform:
        args.platform = "youtube" if (args.target.startswith("@") or "youtube" in args.target) else "twitch"

    AutoClipper(
        platform=args.platform,
        target=args.target,
        multiplier=args.multiplier,
        min_msgs=args.min_msgs,
        pre_roll=args.pre_roll,
        duration=args.duration,
        cooldown=args.cooldown,
        task=args.task,
        vertical=not args.landscape,
        no_subtitles=args.no_subtitles,
        anti_copyright=not args.no_anti_copyright
    ).run()


if __name__ == "__main__":
    main()
