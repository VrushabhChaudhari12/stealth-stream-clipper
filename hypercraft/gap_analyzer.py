"""
Gap & Dramatic Pause Analyzer.
Synthesized from supoclip gap_activity and FireRed-OpenStoryline speech rough-cut.
Differentiates between boring dead air (which kills retention) and intentional dramatic silence / visual action.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple
import numpy as np

GAP_MOTION_SAMPLE_FPS = 4
GAP_FRAME_SIZE = (64, 36)
GAP_MOTION_THRESHOLD = 12.0  # Above this is action/movement (e.g. gameplay, car crash, head turn)
_AUDIO_RATE = 8000
_AUDIO_WINDOW_SEC = 0.05


def get_video_motion_in_range(video_path: str, start: float, end: float) -> float:
    """Calculates median frame-to-frame pixel change during a pause."""
    duration = max(0.1, end - start)
    w, h = GAP_FRAME_SIZE
    cmd = [
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(video_path),
        "-t", f"{duration:.3f}", "-an",
        "-vf", f"fps={GAP_MOTION_SAMPLE_FPS},scale={w}:{h},format=gray",
        "-f", "rawvideo", "-"
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=15)
        if proc.returncode != 0:
            return 0.0
        raw = proc.stdout
        count = len(raw) // (w * h)
        if count < 2:
            return 0.0
        frames = np.frombuffer(raw, dtype=np.uint8).reshape(count, h, w).astype(np.float32)
        diffs = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
        return float(np.median(diffs))
    except Exception:
        return 0.0


def analyze_transcript_gaps(
    words: List[dict],
    video_path: str,
    min_gap_sec: float = 0.40,
    max_kept_dead_air: float = 0.25
) -> List[Tuple[float, float, str]]:
    """
    Analyzes inter-word pauses.
    Returns: List of (gap_start, gap_end, action) where action is:
      - 'PRESERVE_DRAMATIC': High visual action or punchline silence.
      - 'COMPRESS_DEAD_AIR': Static boring silence that should be trimmed.
    """
    if len(words) < 2:
        return []

    actions = []
    for i in range(len(words) - 1):
        w1_end = words[i].get("end", 0.0)
        w2_start = words[i + 1].get("start", 0.0)
        gap_dur = w2_start - w1_end

        if gap_dur >= min_gap_sec:
            motion = get_video_motion_in_range(video_path, w1_end, w2_start)
            # If high motion occurs during silence (e.g. gameplay action, slapstick, shock expression)
            if motion > GAP_MOTION_THRESHOLD:
                actions.append((w1_end, w2_start, "PRESERVE_DRAMATIC"))
            else:
                actions.append((w1_end, w2_start, "COMPRESS_DEAD_AIR"))

    return actions
