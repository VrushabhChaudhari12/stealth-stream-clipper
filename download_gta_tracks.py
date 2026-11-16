"""
GTA Background Music Downloader
Downloads copyright-free / iconic GTA-style instrumental and ambient tracks for stream clipping.
Tracks are saved directly to d:\\GTA clipping\\gta_tracks\\
"""

import os
import sys
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
GTA_TRACKS_DIR = os.path.join(DIR, "gta_tracks")
FFMPEG = os.path.join(DIR, "ffmpeg.exe") if os.path.exists(os.path.join(DIR, "ffmpeg.exe")) else "ffmpeg"

TRACK_TARGETS = [
    ("gta_san_andreas.mp3", "ytsearch1:GTA San Andreas Theme Instrumental copyright free"),
    ("gta_iv_soviet_connection.mp3", "ytsearch1:GTA IV Theme Song Soviet Connection Instrumental"),
    ("gta_vice_city.mp3", "ytsearch1:GTA Vice City Theme Synthwave Instrumental"),
    ("gta_v_pause_menu.mp3", "ytsearch1:GTA V Pause Menu Music short [piano]"),
]


def ensure_tracks(force: bool = False):
    os.makedirs(GTA_TRACKS_DIR, exist_ok=True)
    existing = [f for f in os.listdir(GTA_TRACKS_DIR) if f.lower().endswith((".mp3", ".wav"))]
    print(f"[*] Found {len(existing)} existing tracks in: {GTA_TRACKS_DIR}")
    for f in existing:
        print(f"    - {f}")

    if len(existing) >= len(TRACK_TARGETS) and not force:
        print("[✔] All GTA background tracks are ready.")
        return

    print("[*] Downloading missing tracks via yt-dlp...")
    for filename, query in TRACK_TARGETS:
        target_path = os.path.join(GTA_TRACKS_DIR, filename)
        if os.path.exists(target_path) and not force:
            continue

        print(f"[*] Fetching: {filename} ({query})...")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--default-search", "ytsearch",
            "--ffmpeg-location", FFMPEG,
            "--match-filter", "duration < 360",
            "-x", "--audio-format", "mp3",
            "-o", target_path.replace(".mp3", ".%(ext)s"),
            query
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if os.path.exists(target_path):
                print(f"[✔] Downloaded and ready: {filename}")
            else:
                print(f"[!] Warning: {filename} was not created. Stdout: {res.stdout[-200:]}")
        except Exception as e:
            print(f"[!] Error fetching {filename}: {e}")

    print("[✔] GTA tracks synchronization complete!")


if __name__ == "__main__":
    ensure_tracks("--force" in sys.argv)
