"""
hypercraft/broll_engine.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Automated B-Roll Sourcing and Synthesis Engine.
Fetches high-retention royalty-free vertical footage (Pexels / Pixabay)
or procedurally synthesizes dynamic 1080x1920 cinematic B-roll using FFmpeg.
Inspired by MoneyPrinterTurbo and Hypit.
"""

import os
import urllib.request
import json
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
BROLL_DIR = os.path.join(ROOT_DIR, "clips", "broll_cache")
FFMPEG = os.path.join(ROOT_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(ROOT_DIR, "ffmpeg.exe")) else "ffmpeg"

os.makedirs(BROLL_DIR, exist_ok=True)

# Keyword to B-roll category mapping
BROLL_KEYWORDS = {
    "algorithm": "cyber_matrix",
    "jails": "system_lock",
    "trapped": "system_lock",
    "percent": "analytics_growth",
    "views": "audience_surge",
    "swipe": "glitch_warning",
    "kills": "glitch_warning",
    "loop": "infinite_tunnel"
}


def ensure_procedural_broll():
    """
    Synthesizes a starter library of 1080x1920 60fps cinematic B-roll clips
    using procedural FFmpeg visual generators. Zero API key required.
    """
    generators = {
        "cyber_matrix": (
            "testsrc2=s=1080x1920:r=60,"
            "boxblur=10:2,eq=contrast=1.8:brightness=-0.2:saturation=2.0"
        ),
        "analytics_growth": (
            "smptehdbars=s=1080x1920:r=60,"
            "boxblur=25:3,eq=contrast=1.6:brightness=-0.1:saturation=1.5"
        ),
        "glitch_warning": (
            "color=c=red:s=1080x1920:r=60,"
            "noise=alls=80:allf=t+u,eq=contrast=1.5:brightness=-0.2"
        ),
        "system_lock": (
            "color=c=0x0f172a:s=1080x1920:r=60,"
            "drawbox=x=140:y=600:w=800:h=600:color=red@0.8:t=12"
        ),
        "infinite_tunnel": (
            "mandelbrot=s=1080x1920:r=60:maxiter=120,"
            "eq=contrast=1.4:saturation=1.8:brightness=-0.1"
        )
    }

    for name, filter_graph in generators.items():
        out_path = os.path.join(BROLL_DIR, f"{name}.mp4")
        if not os.path.exists(out_path):
            cmd = [
                FFMPEG, "-y",
                "-f", "lavfi", "-i", filter_graph,
                "-t", "3.0",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                "-pix_fmt", "yuv420p",
                out_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def fetch_pexels_broll(query: str, api_key: str, output_path: str) -> bool:
    """
    Fetches real 9:16 vertical video from Pexels API if API key is provided.
    """
    try:
        url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=1"
        req = urllib.request.Request(url, headers={"Authorization": api_key})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            videos = data.get("videos", [])
            if videos:
                files = videos[0].get("video_files", [])
                # Pick 1080p or 720p vertical
                files = sorted(files, key=lambda x: x.get("width", 0), reverse=True)
                download_url = files[0]["link"]
                urllib.request.urlretrieve(download_url, output_path)
                return True
    except Exception:
        pass
    return False


def get_broll_for_keyword(keyword: str) -> str | None:
    """
    Finds or synthesizes the best matching B-roll video clip for a keyword.
    """
    ensure_procedural_broll()
    clean_k = keyword.lower()
    cat = BROLL_KEYWORDS.get(clean_k)
    if not cat:
        for k, v in BROLL_KEYWORDS.items():
            if k in clean_k:
                cat = v
                break
    if not cat:
        cat = "cyber_matrix"

    local_file = os.path.join(BROLL_DIR, f"{cat}.mp4")
    if os.path.exists(local_file):
        return local_file
    return None
