import os
import subprocess
import json
from faster_whisper import WhisperModel

REF_DIR = "clips/study_refs"
os.makedirs(REF_DIR, exist_ok=True)

shorts = [
    {"id": "OwT8lJOLdwQ", "url": "https://www.youtube.com/shorts/OwT8lJOLdwQ", "tag": "dialogue_humor"},
    {"id": "7dyY3gdJ718", "url": "https://www.youtube.com/shorts/7dyY3gdJ718", "tag": "panic_leak_chaos"},
    {"id": "cuNUhUep7uA", "url": "https://www.youtube.com/shorts/cuNUhUep7uA", "tag": "rage_trolling"},
    {"id": "04l1leEfA8M", "url": "https://www.youtube.com/shorts/04l1leEfA8M", "tag": "sad_prank_betrayal"},
    {"id": "4ACq2HxoJeA", "url": "https://www.youtube.com/shorts/4ACq2HxoJeA", "tag": "deadpan_gaslighting"},
    {"id": "0hafqeSin5I", "url": "https://www.youtube.com/shorts/0hafqeSin5I", "tag": "500iq_clutch"}
]

ffmpeg = r"d:\GTA clipping\ffmpeg.exe"

whisper = WhisperModel("base", device="cpu", compute_type="int8")

dossiers = []

for s in shorts:
    v_id = s["id"]
    print(f"\n==========================================")
    print(f"[*] Studying {v_id} ({s['tag']})...")
    out_video = os.path.join(REF_DIR, f"{v_id}.mp4")
    
    # Download video with yt-dlp
    if not os.path.exists(out_video):
        cmd = ["yt-dlp", "-o", out_video, s["url"]]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    # Also dump metadata
    meta_path = os.path.join(REF_DIR, f"{v_id}_meta.json")
    if not os.path.exists(meta_path):
        meta_cmd = ["yt-dlp", s["url"], "--dump-json"]
        proc = subprocess.run(meta_cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            with open(meta_path, "w", encoding="utf-8") as mf:
                mf.write(proc.stdout)
                
    # Extract audio
    wav_path = os.path.join(REF_DIR, f"{v_id}.wav")
    if not os.path.exists(wav_path):
        cmd_wav = [ffmpeg, "-y", "-i", out_video, "-ar", "16000", "-ac", "1", wav_path]
        subprocess.run(cmd_wav, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    # Transcribe with Whisper
    transcript = []
    if os.path.exists(wav_path):
        segments, _ = whisper.transcribe(wav_path, word_timestamps=True, language="en")
        for seg in segments:
            transcript.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            })
            
    # Extract 4 keyframes
    frame_dir = os.path.join(REF_DIR, f"{v_id}_frames")
    os.makedirs(frame_dir, exist_ok=True)
    for sec in [1.0, 3.5, 7.0, 12.0]:
        frame_file = os.path.join(frame_dir, f"frame_{sec}s.jpg")
        if not os.path.exists(frame_file):
            f_cmd = [ffmpeg, "-y", "-ss", str(sec), "-i", out_video, "-vframes", "1", "-q:v", "2", frame_file]
            subprocess.run(f_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    dossiers.append({
        "id": v_id,
        "tag": s["tag"],
        "transcript": transcript,
        "frames": os.listdir(frame_dir) if os.path.exists(frame_dir) else []
    })

with open(os.path.join(REF_DIR, "study_summary.json"), "w", encoding="utf-8") as f:
    json.dump(dossiers, f, indent=2)

print("\n[✔] Finished downloading and extracting dossiers for all 6 reference shorts!")
