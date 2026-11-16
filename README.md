# 🎬 Stealth Stream Auto-Clipper v4.1 (Enterprise Viral Engine)

Autonomous live stream clipping and publishing pipeline based on real-time chat spike velocity and viral post-production.

- **100% Free & Local**: Zero API or cloud subscription costs. Spike math, video cutting, kinetic subtitles, thumbnail generation, and audio ducking run locally on your PC.
- **Multi-Platform**: Supports **Twitch** (anonymous IRC chat) and **YouTube Live** (e.g., IShowSpeed via pytchat).
- **GTA Background Music Engine**: Mixes iconic GTA instrumental beats (`gta_tracks/`) at subtle background levels with automated sidechain ducking that lowers volume whenever the creator speaks.
- **Automated Post-Upload Cleanup**: Automatically purges raw clips (`_raw.mp4`) and temporary subtitle files (`.ass`, `.srt`) the moment a short is uploaded to YouTube, keeping your drive clean.
- **Viral ASS Subtitles**: Hormozi / MrBeast style kinetic subtitles with rapid 2–3 word bursts, active yellow highlight (`\c&H00FFFF&`), and heavy outline.
- **Clickbait Thumbnails & Titles**: Auto-generates high-contrast 9:16 vertical thumbnails with red arrows and emojis, paired with high-CTR clickbait titles.
- **Direct YouTube Shorts Auto-Uploader**: Direct OAuth 2.0 connection to YouTube Data API v3 for hands-free publishing.
- **Anti-Copyright & Content ID Fingerprint Disruption**: Micro-zoom (1.04x), color saturation grading, rubberband micro-pitch shifting (1.02x), and spectral EQ filtering.

---

## ⚡ Quick Start

### 1. Download / Sync GTA Background Tracks
```powershell
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" download_gta_tracks.py
```

### 2. Connect YouTube Channel (One-Time Setup)
```powershell
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" youtube_uploader.py --auth
```

### 3. Start Autonomous Clipper with Auto-Upload & GTA BGM
```powershell
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" clipper.py --target @IShowSpeed --auto-upload --privacy public
```

---

## ⚙️ Parameters & Tuning

| Flag | Default | Description |
|---|---|---|
| `--target` | Required | Streamer handle, channel name, or YouTube live stream URL |
| `--platform` | Auto | `youtube` or `twitch` (auto-detected from target) |
| `--auto-upload` | `False` | Automatically uploads clips to YouTube Shorts via YouTube Data API |
| `--privacy` | `public` | YouTube privacy status: `public`, `unlisted`, or `private` |
| `--clean-older` | `False` | Immediately purges older raw clips and temporary files across `clips/` |
| `--no-bgm` | `False` | Disables GTA background music mixing |
| `--bgm-volume` | `0.08` | Background music base volume (default: 0.08 = subtle, non-intrusive) |
| `--multiplier` | `2.0` | Chat rate spike threshold (e.g. 2.0x baseline moving average) |
| `--min-msgs` | `8` | Minimum chat messages in the 10-second bucket to trigger |
| `--pre-roll` | `25` | Seconds before the spike to start the clip |
| `--duration` | `50` | Total duration of the extracted clip in seconds |
| `--cooldown` | `90` | Minimum seconds between clips to avoid duplicate triggers |
| `--landscape` | `False` | Outputs standard 16:9 widescreen instead of 9:16 vertical |
| `--no-subtitles`| `False` | Disables Whisper subtitle transcription |
| `--no-anti-copyright`| `False` | Disables anti-copyright pitch/zoom/EQ filters |

---

## 📁 Output Directory (`./clips/<streamer_name>/`)

For each detected hype moment:
1. `clip_YYYYMMDD_HHMMSS_final.mp4` — Final ready-to-post 9:16 vertical Short with active subtitles and ducked GTA BGM.
2. `clip_YYYYMMDD_HHMMSS_thumb.jpg` — 1080x1920 high-contrast vertical thumbnail.
3. `clip_YYYYMMDD_HHMMSS_meta.json` — SEO title, description, and high-reach hashtags.
4. `clip_YYYYMMDD_HHMMSS_credit.txt` — Fair use attribution and streamer credit.
*(Raw `.mp4` and temporary subtitle files are automatically deleted after successful upload).*
