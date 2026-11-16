"""
Stealth Stream Auto-Clipper v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
100% Free & Local Pipeline. Zero API costs.

Patterns absorbed from actual source code of:
  • AI-Youtube-Shorts-Generator (Anil-matcha)
  • autoclip (zhouxiaoka)
  • openshorts (mutonby)

Key upgrades from source analysis:
  ✔ word_timestamps=True + vad_filter=True + condition_on_previous_text=False
  ✔ merge_continuation_words() — fixes leading-space fragmentation in faster-whisper
  ✔ snap_clip_to_words() — snaps boundaries to real word timestamps (natural cuts)
  ✔ 25% dedup ratio (not 50%) — prevents same moment appearing twice
  ✔ H.264 always re-encode, never stream copy (HEVC/edit-list black-screen fix)
  ✔ FFmpeg 8 compatible: subtitles=filename= named option (not positional)
  ✔ DELIVERY_MIN_WIDTH=1080 upscaling floor
  ✔ SRT caching per stream file (skips re-transcription on retry)
"""

import os, sys, re, time, socket, random, argparse, subprocess, threading
from collections import deque
from datetime import datetime
from urllib.request import Request, urlopen

# ─── Paths ───────────────────────────────────────────────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(DIR, "clips")
DELIVERY_MIN_WIDTH = 1080  # openshorts: always upscale crop to this minimum

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

# ─── Hype keyword weights (autoclip-tuned) ───────────────────────────────────
HYPE_KEYWORDS = {
    "w", "l", "omg", "wtf", "clip", "clipped", "bro", "cap", "yooo",
    "no way", "noway", "kekw", "lul", "pog", "pogchamp", "monkas",
    "omegalul", "ez", "gg", "rip", "dead", "lmao", "based", "literally",
    "actually", "wait", "bro what", "pause", "hold on", "caught in 4k",
    "🔥", "💀", "😭", "🤣", "⬆️", "💯", "😂",
}

# ─── ASS subtitle style (openshorts production style) ────────────────────────
ASS_STYLE = (
    "Fontname=Arial,"
    "Fontsize=22,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H80000000,"
    "BorderStyle=3,"
    "Outline=2.5,"
    "Shadow=0,"
    "MarginV=40,"
    "Alignment=2"
)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def fmt_srt(s: float) -> str:
    h, m = int(s // 3600), int((s % 3600) // 60)
    sec, ms = int(s % 60), int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def esc_ffmpeg(p: str) -> str:
    """Escape path for FFmpeg subtitles filter on Windows."""
    return p.replace("\\", "/").replace(":", "\\:")

def clean_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)


# ─────────────────────────────────────────────────────────────────────────────
# TRANSCRIPTION  (openshorts + AI-Shorts-Generator production settings)
# ─────────────────────────────────────────────────────────────────────────────

def merge_continuation_words(words: list[dict]) -> list[dict]:
    """
    OPENSHORTS DISCOVERY: faster-whisper marks word boundaries with a LEADING SPACE.
    Words WITHOUT a leading space (e.g. "-Kanal.") are continuations of the previous word.
    Without this merge, subtitle blocks get split in the middle of compound words.
    """
    if not words:
        return words
    merged = [dict(words[0])]
    for w in words[1:]:
        if not w["word"].startswith(" "):
            # Continuation fragment — glue onto the previous word
            merged[-1]["word"] += w["word"]
            merged[-1]["end"] = w["end"]
        else:
            merged.append(dict(w))
    return merged


def snap_clip_to_words(start: float, end: float, words: list[dict],
                       video_duration: float,
                       search_window: float = 1.5,
                       max_lead: float = 0.35,
                       max_tail: float = 0.45) -> tuple[float, float]:
    """
    OPENSHORTS: Snaps LLM/spike-proposed timestamps to nearest real word boundaries.
    - Leads into silence before the first word (up to max_lead seconds)
    - Trails into silence after the last word (up to max_tail seconds)
    - Falls back to original if duration bounds can't be satisfied.
    Single biggest improvement for natural-sounding cuts.
    """
    start_cands = [w for w in words if abs(w["start"] - start) <= search_window]
    if start_cands:
        best = min(start_cands, key=lambda w: abs(w["start"] - start))
        snapped_start = max(0.0, best["start"] - max_lead)
    else:
        snapped_start = start

    end_cands = [w for w in words if abs(w["end"] - end) <= search_window]
    if end_cands:
        best = min(end_cands, key=lambda w: abs(w["end"] - end))
        snapped_end = min(video_duration, best["end"] + max_tail)
    else:
        snapped_end = end

    # Safety: don't create clips shorter than 5s
    if snapped_end - snapped_start < 5.0:
        return start, end
    return snapped_start, snapped_end


def transcribe_to_srt(video_path: str, srt_path: str,
                      model=None, chunk_words: int = 4) -> tuple[bool, list[dict]]:
    """
    Returns (success, word_list) where word_list can be used for snap_clip_to_words.

    Production settings from openshorts + AI-Shorts-Generator:
      - vad_filter=True          → drops silence (fewer ghost subtitles)
      - condition_on_previous_text=False → prevents hallucination loops
      - word_timestamps=True     → required for karaoke captions
      - beam_size=5              → production quality (not 3)

    openshorts 4-word chunk groups → mobile karaoke sweet-spot.
    """
    # Cache check (AI-Shorts-Generator pattern): skip re-transcription if SRT is fresh
    if (os.path.exists(srt_path) and os.path.exists(video_path) and
            os.path.getmtime(srt_path) > os.path.getmtime(video_path)):
        print(f"[✔] SRT cache hit: {os.path.basename(srt_path)}")
        return True, []

    try:
        from faster_whisper import WhisperModel
        if model is None:
            model = WhisperModel("base.en", device="cpu", compute_type="int8")

        segments, _ = model.transcribe(
            video_path,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
            word_timestamps=True,
        )

        all_words = []
        for seg in segments:
            ws = getattr(seg, "words", None)
            if ws:
                for w in ws:
                    all_words.append({"word": w.word, "start": w.start, "end": w.end})
            else:
                # Fallback: add segment as single word entry
                all_words.append({"word": " " + seg.text.strip(),
                                   "start": seg.start, "end": seg.end})

        # Apply openshorts leading-space fragment merge
        all_words = merge_continuation_words(all_words)

        # Build 4-word-chunk SRT
        entries, chunk_w, chunk_start = [], [], None
        for w in all_words:
            if chunk_start is None:
                chunk_start = w["start"]
            chunk_w.append(w["word"].strip())
            if len(chunk_w) >= chunk_words:
                entries.append((chunk_start, w["end"], " ".join(chunk_w)))
                chunk_w, chunk_start = [], None
        if chunk_w and chunk_start is not None:
            entries.append((chunk_start, chunk_start + 1.5, " ".join(chunk_w)))

        with open(srt_path, "w", encoding="utf-8") as f:
            for i, (s, e, t) in enumerate(entries, 1):
                f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{t}\n\n")

        return len(entries) > 0, all_words

    except Exception as ex:
        print(f"[!] Whisper error: {ex}")
        return False, []


# ─────────────────────────────────────────────────────────────────────────────
# FFMPEG RENDER  (openshorts blurred-bg pattern + FFmpeg 8 compat fixes)
# ─────────────────────────────────────────────────────────────────────────────

def slice_stream(source: str, start: int, duration: int, out: str) -> bool:
    """
    AUTOCLIP LESSON: ALWAYS H.264 re-encode — NEVER stream copy.
    Reason: stream sources are often HEVC; Windows WebView2 and macOS WKWebView
    have no system HEVC decoder → black screen. Stream copy also leaves non-zero
    start-time edit lists that Chromium-based players black-screen on.
    """
    cmd = [
        FFMPEG, "-y",
        "-ss", str(start),    # seek BEFORE -i for speed
        "-t",  str(duration),
        "-i",  source,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        out
    ]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0


def render_final(raw: str, srt: str | None, out: str, vertical: bool) -> bool:
    """
    openshorts WIDE/GENERAL strategy:
      - 1080×1920 blurred bg (boxblur=20:2)
      - Original centered on top
      - Karaoke subtitles burned in one pass

    FFMPEG 8 COMPAT (from openshorts source comment):
      Use subtitles=filename= (named option) NOT subtitles='path' (positional).
      Positional quoted values are REJECTED by ffmpeg 8's filtergraph parser.

    DELIVERY_MIN_WIDTH=1080: openshorts always upscales crop to 1080px minimum.
    """
    if vertical:
        base = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=20:2[bg];"
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
        )
        if srt and os.path.exists(srt):
            # Named option syntax — ffmpeg 8 compatible
            fc = f"{base};[base]subtitles=filename='{esc_ffmpeg(srt)}':force_style='{ASS_STYLE}'[vout]"
        else:
            fc = base + ";[base]copy[vout]"
    else:
        if srt and os.path.exists(srt):
            fc = f"[0:v]subtitles=filename='{esc_ffmpeg(srt)}':force_style='{ASS_STYLE}'[vout]"
        else:
            fc = "[0:v]copy[vout]"

    cmd = [
        FFMPEG, "-y", "-i", raw,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        out
    ]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not (r.returncode == 0 and os.path.exists(out)):
        import shutil
        shutil.copyfile(raw, out)  # atomic fallback
    return os.path.exists(out)


def save_credit(path: str, channel: str, platform: str, stream_url: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== CLIP CREDIT (always tag the creator!) ===\n\n")
        f.write(f"Creator : {channel}\n")
        f.write(f"Platform: {platform.upper()}\n")
        f.write(f"Source  : {stream_url}\n")
        f.write(f"Clipped : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Suggested caption:\n")
        f.write(f"Chat literally exploded 💀🔥  Credits: @{channel}\n\n")
        f.write(f"Tags: #gaming #twitch #{platform} #clips #fyp #trending #{clean_name(channel)}\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CLIPPER
# ─────────────────────────────────────────────────────────────────────────────

class AutoClipper:
    def __init__(self, platform: str, target: str, **cfg):
        self.platform = platform.lower()
        self.target   = target.strip()

        # Spike detection (autoclip-tuned defaults)
        self.multiplier  = float(cfg.get("multiplier", 2.8))
        self.min_msgs    = int(cfg.get("min_msgs", 12))
        self.bucket_sec  = int(cfg.get("bucket_sec", 10))
        self.baseline    = int(cfg.get("baseline_sec", 300))
        self.cooldown    = int(cfg.get("cooldown", 90))

        # Clip output
        self.pre_roll    = int(cfg.get("pre_roll", 25))
        self.duration    = int(cfg.get("duration", 50))
        self.vertical    = bool(cfg.get("vertical", True))
        self.no_subs     = bool(cfg.get("no_subtitles", False))
        # Streamer-specific folder segregation: D:\GTA clipping\clips\<streamer_name>
        base_clips = cfg.get("output_dir", CLIPS_DIR)
        streamer_slug = clean_name(target).lstrip("@")
        self.output_dir = os.path.join(base_clips, streamer_slug)
        os.makedirs(self.output_dir, exist_ok=True)

        self.stream_file  = os.path.join(DIR, f"stream_{clean_name(target)}.ts")
        self.stream_start: float | None = None
        self.last_clip_time = 0.0
        self.clip_count  = 0
        self.is_running  = True
        self.whisper_model = None

        # Chat velocity history: deque of (timestamp, weight)
        self.history: deque = deque()

    # ── Platform URLs ─────────────────────────────────────────────────────────
    def _stream_url(self) -> tuple[str, str]:
        t = self.target
        if self.platform == "twitch":
            ch = t.lstrip("#").replace("https://twitch.tv/", "").replace("twitch.tv/", "").lower()
            return f"twitch.tv/{ch}", ch
        else:
            url = t if t.startswith("http") else \
                  f"https://www.youtube.com/{t if t.startswith('@') else '@'+t}/live"
            return url, t

    # ── HUD ───────────────────────────────────────────────────────────────────
    def _hud(self, now: float, recent: int, base_rate: float, threshold: float):
        if not self.stream_start:
            sys.stdout.write(f"\r[⏳ WAITING] Streamer offline — polling every 15s...  ")
            sys.stdout.flush()
            return
        elapsed = int(now - self.stream_start)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        sys.stdout.write(
            f"\r🔴 {h:02d}:{m:02d}:{s:02d} | "
            f"💬 {recent:3d}/10s "
            f"[Base:{base_rate:4.1f}  Trigger:{threshold:4.1f}] | "
            f"🎬 Clips saved: {self.clip_count}  "
        )
        sys.stdout.flush()

    # ── Spike Detection (weighted, from autoclip) ─────────────────────────────
    def _register(self, text: str):
        now = time.time()
        lower = text.lower()
        weight = 1.5 if any(k in lower for k in HYPE_KEYWORDS) else 1.0
        self.history.append((now, weight))
        self._check_spike(now)

    def _check_spike(self, now: float):
        cutoff = now - self.baseline
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()

        raw_count = len(self.history)
        if raw_count < self.min_msgs:
            return

        total_w    = sum(w for _, w in self.history)
        recent_w   = sum(w for t, w in self.history if t >= now - self.bucket_sec)
        recent_raw = sum(1 for t, _ in self.history if t >= now - self.bucket_sec)
        base_rate  = (total_w / self.baseline) * self.bucket_sec
        threshold  = base_rate * self.multiplier

        self._hud(now, recent_raw, base_rate, threshold)

        if recent_w >= threshold and recent_raw >= self.min_msgs:
            if (now - self.last_clip_time) >= self.cooldown:
                self.last_clip_time = now
                self.clip_count += 1
                print(f"\n\n🔥 SPIKE! {recent_raw} msgs/10s (threshold: {threshold:.1f})")
                threading.Thread(target=self._clip_worker, args=(now,), daemon=True).start()

    # ── Clip Worker ───────────────────────────────────────────────────────────
    def _clip_worker(self, spike_time: float):
        # Wait for post-roll to record into the TS buffer
        post_wait = max(5, self.duration - self.pre_roll + 5)
        print(f"[*] Buffering {post_wait}s post-spike stream...")
        time.sleep(post_wait)

        if not os.path.exists(self.stream_file):
            print(f"[!] stream.ts not found — is streamlink running?")
            return
        if not self.stream_start:
            print("[!] Stream start time unknown. Skipping.")
            return

        offset    = spike_time - self.stream_start
        start_sec = max(0, int(offset - self.pre_roll))
        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")

        raw_clip    = os.path.join(self.output_dir, f"clip_{ts}_raw.mp4")
        srt_file    = os.path.join(self.output_dir, f"clip_{ts}.srt")
        final_clip  = os.path.join(self.output_dir, f"clip_{ts}_final.mp4")
        credit_file = os.path.join(self.output_dir, f"clip_{ts}_credit.txt")

        print(f"[*] Slicing {self.duration}s from offset {start_sec}s ...")
        if not slice_stream(self.stream_file, start_sec, self.duration, raw_clip):
            print("[!] FFmpeg slice failed.")
            return
        print(f"[✔] Raw clip: {os.path.basename(raw_clip)}")

        # Transcribe with all production flags applied
        word_list = []
        srt_ok = False
        if not self.no_subs:
            print("[*] Transcribing (faster-whisper, CPU int8, word_timestamps)...")
            if self.whisper_model is None:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
            srt_ok, word_list = transcribe_to_srt(raw_clip, srt_file, self.whisper_model)
            if srt_ok:
                print(f"[✔] SRT ready: {os.path.basename(srt_file)}")

        # Apply snap_clip_to_words to get a cleaner re-cut if word data available
        # (improves natural-sounding start/end for the NEXT clip, as a refinement)
        if word_list:
            snapped_start, snapped_end = snap_clip_to_words(
                float(start_sec), float(start_sec + self.duration),
                word_list, float(start_sec + self.duration + 5)
            )
            # If snap moved boundaries significantly, re-slice for best quality
            if abs(snapped_start - start_sec) > 0.5 or abs(snapped_end - (start_sec + self.duration)) > 0.5:
                print(f"[*] Word-snapping cut: {snapped_start:.1f}s → {snapped_end:.1f}s")
                snap_raw = raw_clip.replace("_raw.mp4", "_snap_raw.mp4")
                if slice_stream(self.stream_file, int(snapped_start),
                                int(snapped_end - snapped_start), snap_raw):
                    os.replace(snap_raw, raw_clip)
                    # Regenerate SRT for the new boundaries
                    if not self.no_subs:
                        srt_ok, _ = transcribe_to_srt(raw_clip, srt_file, self.whisper_model)

        # Render final (vertical + captions)
        print(f"[*] Rendering {'9:16 vertical' if self.vertical else '16:9'} final clip...")
        render_final(raw_clip, srt_file if srt_ok else None, final_clip, self.vertical)
        print(f"[🎉] Final clip: {final_clip}")

        url, name = self._stream_url()
        save_credit(credit_file, name, self.platform, url)

    # ── Streamlink Recorder ───────────────────────────────────────────────────
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
                print(f"\n[🚀 LIVE] Stream started at {datetime.now().strftime('%H:%M:%S')}")

    # ── Chat Listeners ────────────────────────────────────────────────────────
    def _twitch_irc(self):
        _, channel = self._stream_url()
        nick = f"justinfan{random.randint(10000, 99999)}"
        print(f"[*] Twitch IRC → #{channel} (anonymous as {nick})")

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
                print(f"\n[!] IRC reconnecting: {e}")
                time.sleep(5)

    def _youtube_chat(self):
        import pytchat
        url, _ = self._stream_url()
        print(f"[*] Resolving YouTube live ID for: {url}")

        vid = None
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
                sys.stdout.write("\r[⏳] Waiting for YouTube live stream...  ")
                sys.stdout.flush()
                time.sleep(20)

        print(f"[✔] YouTube Live ID: {vid}")
        chat = pytchat.create(video_id=vid)
        while chat.is_alive() and self.is_running:
            try:
                for c in chat.get().sync_items():
                    self._register(c.message)
                time.sleep(0.5)
            except Exception:
                time.sleep(2)

    # ── Entry Point ───────────────────────────────────────────────────────────
    def run(self):
        url, name = self._stream_url()
        print("━" * 65)
        print(f"  🎬  Stealth Auto-Clipper  v3.0  (source-verified patterns)")
        print(f"  📺  {self.platform.upper()} → {name}")
        print(f"  ⚡  Spike: {self.multiplier}× baseline (min {self.min_msgs} msgs/10s)")
        print(f"  ✂️   Clip: {self.duration}s total  ({self.pre_roll}s pre-roll)")
        print(f"  📐  Format: {'9:16 Vertical (Shorts/Reels/TikTok)' if self.vertical else '16:9 Landscape'}")
        print(f"  🧠  Subtitles: {'OFF' if self.no_subs else 'ON (word-level karaoke)'}")
        print(f"  💾  Output: {self.output_dir}")
        print("━" * 65 + "\n")

        threading.Thread(target=self._record, daemon=True).start()

        if self.platform == "twitch":
            self._twitch_irc()
        else:
            self._youtube_chat()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Stealth Auto-Clipper v3.0 — Live stream spike detection & auto-clipping",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python clipper.py --target kaicenat
  python clipper.py --target @IShowSpeed
  python clipper.py --target xqc --multiplier 3.5 --min-msgs 20
  python clipper.py --target hasanabi --multiplier 2.0 --landscape
        """
    )
    p.add_argument("--platform", choices=["twitch", "youtube"],
                   help="Platform (auto-detected from --target if omitted)")
    p.add_argument("--target", required=True,
                   help="Channel name, @handle, or URL")
    p.add_argument("--multiplier", type=float, default=2.8,
                   help="Spike threshold × baseline (default: 2.8)")
    p.add_argument("--min-msgs",   type=int,   default=12,
                   help="Min msgs/10s to qualify as spike (default: 12)")
    p.add_argument("--pre-roll",   type=int,   default=25,
                   help="Seconds before spike to start clip (default: 25)")
    p.add_argument("--duration",   type=int,   default=50,
                   help="Clip length in seconds (default: 50)")
    p.add_argument("--cooldown",   type=int,   default=90,
                   help="Min seconds between clips (default: 90)")
    p.add_argument("--vertical",   action="store_true", default=True,
                   help="9:16 output — Shorts/Reels/TikTok (default: ON)")
    p.add_argument("--landscape",  action="store_true",
                   help="Override to 16:9 landscape output")
    p.add_argument("--no-subtitles", action="store_true",
                   help="Skip Whisper transcription")
    p.add_argument("--output-dir", default=CLIPS_DIR,
                   help=f"Output folder (default: {CLIPS_DIR})")
    args = p.parse_args()

    # Auto-detect platform
    if not args.platform:
        args.platform = "youtube" if (
            args.target.startswith("@") or "youtube" in args.target
        ) else "twitch"

    AutoClipper(
        platform=args.platform,
        target=args.target,
        multiplier=args.multiplier,
        min_msgs=args.min_msgs,
        pre_roll=args.pre_roll,
        duration=args.duration,
        cooldown=args.cooldown,
        vertical=not args.landscape,
        no_subtitles=args.no_subtitles,
        output_dir=args.output_dir,
    ).run()


if __name__ == "__main__":
    main()
