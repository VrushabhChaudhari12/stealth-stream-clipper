# 🎬 Stealth Stream Auto-Clipper v4.2 (Enterprise Viral Engine)

Autonomous live stream clipping and publishing pipeline based on real-time chat spike velocity and viral post-production.

- **100% Free & Local**: Zero API or cloud subscription costs. Spike math, video cutting, kinetic subtitles, thumbnail generation, and audio ducking run locally on your PC.
- **2026 Viral Engine Rules**: Built to the exact specifications in [VIRAL_RULES.md](file:///d:/GTA%20clipping/VIRAL_RULES.md) (25–45s sweet spot, 4-beat spine, 40–60 char titles, 4-tier hashtag architecture).
- **vidIQ MCP Integration**: Native MCP server integration with `https://mcp.vidiq.com/mcp` for real-time YouTube keyword analytics, retention tracking, and competitor intelligence.
- **GTA Background Music Engine**: Mixes iconic GTA instrumental beats (`gta_tracks/`) at subtle background levels with automated sidechain ducking that lowers volume whenever the creator speaks.
- **Automated Post-Upload Cleanup**: Automatically purges raw clips (`_raw.mp4`) and temporary subtitle files (`.ass`, `.srt`) the moment a short is uploaded to YouTube, keeping your drive clean.
- **Viral ASS Subtitles**: Hormozi / MrBeast style kinetic subtitles with rapid 2–3 word bursts, active yellow highlight (`\c&H00FFFF&`), and heavy outline.
- **Complimentary Thumbnails & Titles**: 3–4 word high-contrast thumbnail punch phrases that compliment (never duplicate) the 40–60 character mobile-optimized title.
- **Direct YouTube Shorts Auto-Uploader**: Direct OAuth 2.0 connection to YouTube Data API v3 for hands-free publishing.
- **Anti-Copyright & Content ID Fingerprint Disruption**: Punch-in zoom (1.14x), color saturation grading (+12%), rubberband micro-pitch shifting (1.02x), and spectral EQ filtering.

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
& "C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe" clipper.py --target "@IShowSpeed" --auto-upload --privacy public
```

---

## ⚙️ Parameters & Tuning

| Flag | Default | Description |
|---|---|---|
| `--target` | Required | Streamer handle, channel name, or YouTube live stream URL (wrap in quotes) |
| `--platform` | Auto | `youtube` or `twitch` (auto-detected from target) |
| `--auto-upload` | `False` | Automatically uploads clips to YouTube Shorts via YouTube Data API |
| `--privacy` | `public` | YouTube privacy status: `public`, `unlisted`, or `private` |
| `--clean-older` | `False` | Immediately purges older raw clips and temporary files across `clips/` |
| `--no-bgm` | `False` | Disables GTA background music mixing |
| `--bgm-volume` | `0.08` | Background music base volume (default: 0.08 = subtle, non-intrusive) |
| `--multiplier` | `2.0` | Chat rate spike threshold (e.g. 2.0x baseline moving average) |
| `--min-msgs` | `8` | Minimum chat messages in the 10-second bucket to trigger |
| `--pre-roll` | `15` | Seconds before the spike to start the clip |
| `--duration` | `35` | Total duration of the extracted clip in seconds (25–45s sweet spot) |
| `--cooldown` | `90` | Minimum seconds between clips to avoid duplicate triggers |
| `--landscape` | `False` | Outputs standard 16:9 widescreen instead of 9:16 vertical |
| `--no-subtitles`| `False` | Disables Whisper subtitle transcription |
| `--no-anti-copyright`| `False` | Disables anti-copyright pitch/zoom/EQ filters |

---

## 📁 Output Directory (`./clips/<streamer_name>/`)

For each detected hype moment:
1. `clip_YYYYMMDD_HHMMSS_final.mp4` — Final ready-to-post 9:16 vertical Short with active subtitles and ducked GTA BGM.
2. `clip_YYYYMMDD_HHMMSS_thumb.jpg` — 1080x1920 high-contrast vertical thumbnail.
3. `clip_YYYYMMDD_HHMMSS_meta.json` — SEO title (40–60 chars), 4-tier hashtags, description, and source link.
4. `clip_YYYYMMDD_HHMMSS_credit.txt` — Fair use attribution and streamer credit.
*(Raw `.mp4` and temporary subtitle files are automatically deleted after successful upload).*
