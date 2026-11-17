import os
import subprocess
import json
from faster_whisper import WhisperModel

REF_DIR = "clips/study_refs"
ffmpeg = r"d:\GTA clipping\ffmpeg.exe"
whisper = WhisperModel("base", device="cpu", compute_type="int8")

vids = [
    ("OwT8lJOLdwQ", "dialogue_humor", "OwT8lJOLdwQ.mp4.webm"),
    ("7dyY3gdJ718", "panic_leak_chaos", "7dyY3gdJ718.mp4.webm"),
    ("cuNUhUep7uA", "rage_trolling", "cuNUhUep7uA.mp4.webm"),
    ("04l1leEfA8M", "sad_prank_betrayal", "04l1leEfA8M.mp4.webm"),
    ("4ACq2HxoJeA", "deadpan_gaslighting", "4ACq2HxoJeA.mp4.webm"),
    ("0hafqeSin5I", "500iq_clutch", "0hafqeSin5I.mp4.webm")
]

detailed_dossiers = {}

for vid_id, tag, fname in vids:
    vid_path = os.path.join(REF_DIR, fname)
    if not os.path.exists(vid_path):
        # find matching file
        for f in os.listdir(REF_DIR):
            if f.startswith(vid_id) and f.endswith((".mp4", ".webm")):
                vid_path = os.path.join(REF_DIR, f)
                break
                
    wav_path = os.path.join(REF_DIR, f"{vid_id}.wav")
    cmd_wav = [ffmpeg, "-y", "-i", vid_path, "-ar", "16000", "-ac", "1", wav_path]
    subprocess.run(cmd_wav, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Transcribe
    segments, _ = whisper.transcribe(wav_path, word_timestamps=True, language="en")
    trans_list = []
    for s in segments:
        trans_list.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        
    # Frames
    frame_dir = os.path.join(REF_DIR, f"{vid_id}_frames")
    os.makedirs(frame_dir, exist_ok=True)
    frames = []
    for t in [1.0, 3.5, 7.0, 11.0, 15.0]:
        fr_name = f"frame_{t}s.jpg"
        fr_path = os.path.join(frame_dir, fr_name)
        cmd_fr = [ffmpeg, "-y", "-ss", str(t), "-i", vid_path, "-vframes", "1", "-q:v", "2", fr_path]
        subprocess.run(cmd_fr, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(fr_path):
            frames.append(fr_name)
            
    # Load meta
    meta_path = os.path.join(REF_DIR, f"{vid_id}_meta.json")
    meta = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                m_data = json.load(mf)
                meta = {
                    "title": m_data.get("title"),
                    "view_count": m_data.get("view_count"),
                    "like_count": m_data.get("like_count"),
                    "duration": m_data.get("duration"),
                    "channel": m_data.get("channel"),
                    "description": m_data.get("description", "")[:200]
                }
        except Exception:
            pass
            
    detailed_dossiers[vid_id] = {
        "tag": tag,
        "meta": meta,
        "transcript": trans_list,
        "frames": frames
    }

with open(os.path.join(REF_DIR, "detailed_dossiers.json"), "w", encoding="utf-8") as f:
    json.dump(detailed_dossiers, f, indent=2)

print("[✔] Successfully extracted detailed dossiers for all 6 reference shorts!")
