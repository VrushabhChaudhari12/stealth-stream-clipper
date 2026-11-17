"""
Split-Screen Viral Layout Engine.
Inspired by supoclip reaction_layout.py and 100M+ view reference Shorts (cuNUhUep7uA & 4ACq2HxoJeA).
Provides:
1. Streamer Reaction Layout:
   - Top: Isolated Streamer Facecam (cropped, centered via YuNet face tracking).
   - Bottom: Full Gameplay / In-game action.
2. Duo Split Layout (Top: Content/Interview, Bottom: Secondary Gameplay like GTA Mega Ramp).
3. Standard 9:16 Full Screen with smart pan-and-scan.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np
from .face_tracker import FaceTracker

OUT_W = 1080
OUT_H = 1920
TOP_H = 720        # Top frame height
BOTTOM_H = 1200    # Bottom frame height


class SplitScreenEngine:
    def __init__(self):
        self.face_tracker = FaceTracker()

    def build_reaction_split_filter(
        self,
        video_path: str,
        facecam_box: Optional[tuple] = None,
        top_ratio: float = 0.38
    ) -> Dict[str, Any]:
        """
        Builds FFmpeg filter graph to split a 16:9 gaming video into:
        - Top: Streamer Facecam (auto-detected or provided)
        - Bottom: Gameplay screen
        """
        cap = cv2.VideoCapture(video_path)
        src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
        src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        cap.release()

        top_h = int(OUT_H * top_ratio) // 2 * 2       # e.g. 728
        bottom_h = OUT_H - top_h                       # e.g. 1192

        # If facecam_box not provided, detect facecam
        if facecam_box is None:
            samples = self.face_tracker.sample_video_faces(video_path, num_samples=12)
            face = self.face_tracker.find_reactor_face(src_w, src_h, samples)
            if face:
                fx, fy, fw, fh = face
                # Expand box around face to get full webcam rectangle (with shoulders & mic)
                cx, cy = fx + fw / 2, fy + fh / 2
                cam_w = min(src_w, fw * 2.5)
                cam_h = min(src_h, fh * 2.8)
                crop_x = max(0, min(src_w - cam_w, cx - cam_w / 2))
                crop_y = max(0, min(src_h - cam_h, cy - cam_h * 0.45))
                facecam_box = (int(crop_x), int(crop_y), int(cam_w), int(cam_h))
            else:
                # Default right or left corner fallback for facecam
                facecam_box = (int(src_w * 0.70), int(src_h * 0.05), int(src_w * 0.28), int(src_h * 0.45))

        fc_x, fc_y, fc_w, fc_h = facecam_box
        fc_w = fc_w // 2 * 2
        fc_h = fc_h // 2 * 2

        # Gameplay crop (center 16:9 content)
        game_w = src_w
        game_h = src_h

        # FFmpeg filtergraph:
        # [0:v] split into [cam_in] and [game_in]
        # [cam_in] crop to facecam -> scale to OUT_W x top_h -> [top]
        # [game_in] scale/crop to OUT_W x bottom_h -> [bottom]
        # vstack [top][bottom] -> [v_split]
        # draw dividing border line at top_h
        filter_graph = (
            f"[0:v]split=2[cam_in][game_in];"
            f"[cam_in]crop={fc_w}:{fc_h}:{fc_x}:{fc_y},"
            f"scale={OUT_W}:{top_h}:flags=lanczos,setsar=1[top];"
            f"[game_in]scale={OUT_W}:{bottom_h}:force_original_aspect_ratio=increase,"
            f"crop={OUT_W}:{bottom_h},setsar=1[bottom];"
            f"[top][bottom]vstack=inputs=2[v_stacked];"
            f"[v_stacked]drawbox=y={top_h-2}:w={OUT_W}:h=4:color=#FFD700@0.8:t=fill[v_split]"
        )

        return {
            "filter_graph": filter_graph,
            "output_label": "[v_split]",
            "caption_y": top_h + 40,   # Position captions directly below the split bar
            "top_h": top_h,
            "bottom_h": bottom_h
        }
