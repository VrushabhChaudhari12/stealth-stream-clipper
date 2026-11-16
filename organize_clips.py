"""
Background file organizer:
Automatically watches D:\GTA clipping\clips and moves any loose clips
into their respective streamer subfolder (e.g., M_YADAV_is_LIVE).
"""
import os
import time
import shutil

CLIPS_DIR = r"D:\GTA clipping\clips"
TARGET_STREAMER = "M_YADAV_is_LIVE"

streamer_dir = os.path.join(CLIPS_DIR, TARGET_STREAMER)
os.makedirs(streamer_dir, exist_ok=True)

print(f"[*] Clip organizer watching {CLIPS_DIR} -> {streamer_dir}")

while True:
    try:
        for fname in os.listdir(CLIPS_DIR):
            fpath = os.path.join(CLIPS_DIR, fname)
            # Only move files, not directories
            if os.path.isfile(fpath) and fname.startswith("clip_"):
                # Wait 2 seconds to make sure ffmpeg/whisper is done writing
                time.sleep(2)
                dest = os.path.join(streamer_dir, fname)
                shutil.move(fpath, dest)
                print(f"[✔] Moved {fname} -> {TARGET_STREAMER}/")
    except Exception as e:
        pass
    time.sleep(5)
