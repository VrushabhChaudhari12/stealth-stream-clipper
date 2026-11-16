# 🎬 Stealth Stream Auto-Clipper (100% Free & Local)

Autonomous live stream clipping pipeline based on real-time chat spike velocity.

- **Zero API Costs**: No Claude Code or LLM token expenses. All spike math, cutting, and captioning run locally on your hardware.
- **Multi-Platform**: Supports **Twitch** (anonymous IRC chat) and **YouTube Live** (e.g., IShowSpeed via pytchat).
- **Automated AI Subtitles**: Transcribes audio and burns TikTok/Reels style subtitles using local `faster-whisper` and `ffmpeg`.
- **9:16 Vertical Video**: Optional auto-crop with blurred background for YouTube Shorts, Instagram Reels, and TikTok.
- **Creator Attribution**: Automatically generates credit metadata and social media hashtags for every clip.

---

## ⚡ Quick Start

### 1. Interactive Launch
Double-click `start_clipper.bat` and follow the prompts.

### 2. Command Line (Twitch)
```powershell
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" clipper.py --platform twitch --target kaicenat --vertical
```

### 3. Command Line (YouTube Live - e.g. IShowSpeed)
```powershell
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" clipper.py --platform youtube --target @IShowSpeed --vertical
```

---

## ⚙️ Parameters & Tuning

| Flag | Default | Description |
|---|---|---|
| `--multiplier` | `2.8` | Chat rate spike threshold (e.g. 2.8x the 5-minute moving average) |
| `--min-msgs` | `12` | Minimum messages in the 10-second bucket to avoid dead-chat false triggers |
| `--pre-roll` | `25` | Seconds before the spike to start the clip (captures the action before chat reacts) |
| `--duration` | `50` | Total duration of the extracted clip in seconds |
| `--cooldown` | `90` | Minimum seconds between clips to avoid duplicate triggers during long hype moments |
| `--vertical` | `False` | Formats output as 9:16 vertical video with blurred top/bottom padding |
| `--no-subtitles`| `False` | Skips Whisper subtitle transcription if you only want raw video |

---

## 📁 Output Directory (`./clips`)

For each detected hype moment, the tool produces:
1. `clip_YYYYMMDD_HHMMSS_final.mp4` — Final ready-to-post video (subtitled & formatted).
2. `clip_YYYYMMDD_HHMMSS_raw.mp4` — Clean unedited stream slice.
3. `clip_YYYYMMDD_HHMMSS.srt` — Timestamped transcript.
4. `clip_YYYYMMDD_HHMMSS_credit.txt` — Streamer credit, channel link, and suggested social tags.
