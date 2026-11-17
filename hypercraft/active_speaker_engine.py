"""
Active Speaker Tracking & Dynamic Multi-Face Switcher Engine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Automatically identifies all speaking faces in multi-person, podcast,
stream collab, or dual-webcam video. Correlates sub-second mouth & facial
movement with speech turns to dynamically switch cameras to whoever is
actively talking, matching viral podcast and streamer shorts editing standards.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import cv2
import numpy as np
from .face_tracker import FaceTracker

OUT_W = 1080
OUT_H = 1920
DEFAULT_TOP_H = 728
DEFAULT_BOTTOM_H = 1192
MIN_TURN_SECONDS = 1.0  # Prevents rapid camera flickering on micro-pauses


class ActiveSpeakerEngine:
    def __init__(self, sample_fps: float = 10.0):
        self.sample_fps = sample_fps
        self.tracker = FaceTracker()

    def discover_face_clusters(
        self,
        video_path: str,
        num_samples: int = 24,
        max_clusters: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Samples video to find all stable, recurring face positions across the video.
        Returns list of clusters with median face center, size, and expanded crop box.
        """
        cap = cv2.VideoCapture(video_path)
        src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
        src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        cap.release()

        samples = self.tracker.sample_video_faces(video_path, num_samples=num_samples)
        if not samples:
            return []

        all_detections = []
        for t, faces in samples:
            for f in faces:
                # Filter out microscopic noise
                if (f[2] * f[3]) / (src_w * src_h) >= 0.0015:
                    all_detections.append((f[0] + f[2] / 2, f[1] + f[3] / 2, f[2], f[3]))

        if not all_detections:
            return []

        # Sort detections horizontally by center X
        sorted_dets = sorted(all_detections, key=lambda d: d[0])
        groups: List[List[Tuple[float, float, float, float]]] = [[sorted_dets[0]]]
        for det in sorted_dets[1:]:
            # If distance to previous cluster center X is > 15% frame width, new cluster
            if det[0] - groups[-1][-1][0] > src_w * 0.15:
                groups.append([det])
            else:
                groups[-1].append(det)

        # Keep clusters with sufficient presence (at least 20% of samples)
        min_support = max(2, int(len(samples) * 0.20))
        valid_groups = [g for g in groups if len(g) >= min_support]
        if not valid_groups:
            valid_groups = groups[:max_clusters]

        clusters = []
        for idx, group in enumerate(valid_groups[:max_clusters]):
            arr = np.asarray(group)
            cx = float(np.median(arr[:, 0]))
            cy = float(np.median(arr[:, 1]))
            fw = float(np.median(arr[:, 2]))
            fh = float(np.median(arr[:, 3]))

            # Expand box for head and shoulders
            cam_w = min(src_w, int(fw * 2.8)) // 2 * 2
            cam_h = min(src_h, int(fh * 2.8)) // 2 * 2
            cam_x = max(0, min(src_w - cam_w, int(cx - cam_w / 2))) // 2 * 2
            cam_y = max(0, min(src_h - cam_h, int(cy - cam_h * 0.42))) // 2 * 2

            clusters.append({
                "id": idx,
                "label": f"Speaker_{idx+1}",
                "cx": cx,
                "cy": cy,
                "fw": fw,
                "fh": fh,
                "crop_box": (cam_x, cam_y, cam_w, cam_h),
                "support": len(group)
            })

        return clusters

    def track_mouth_motion_series(
        self,
        video_path: str,
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Samples video at sample_fps and calculates optical frame-to-frame delta
        in the mouth region (bottom half) of each face cluster.
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        prev_mouths = {c["id"]: None for c in clusters}
        motion_series = {c["id"]: [] for c in clusters}
        timestamps = []

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            if frame_idx % step == 0:
                t = frame_idx / fps
                timestamps.append(t)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                for c in clusters:
                    cid = c["id"]
                    cx, cy = int(c["cx"]), int(c["cy"])
                    fw, fh = int(c["fw"]), int(c["fh"])
                    # Mouth region: lower 55% of face
                    y1 = max(0, cy)
                    y2 = min(gray.shape[0], int(cy + fh * 0.55))
                    x1 = max(0, int(cx - fw * 0.38))
                    x2 = min(gray.shape[1], int(cx + fw * 0.38))

                    roi = gray[y1:y2, x1:x2]
                    score = 0.0
                    prev = prev_mouths[cid]
                    if prev is not None and prev.shape == roi.shape:
                        score = float(np.mean(np.abs(roi.astype(np.float32) - prev.astype(np.float32))))
                    motion_series[cid].append(score)
                    prev_mouths[cid] = roi

            frame_idx += 1

        cap.release()
        return {
            "timestamps": np.asarray(timestamps),
            "motion": {cid: np.asarray(scores) for cid, scores in motion_series.items()}
        }

    def compute_speaker_turns(
        self,
        video_path: str,
        duration: float,
        transcript_words: Optional[List[dict]] = None,
        min_turn_sec: float = MIN_TURN_SECONDS
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Determines the dynamic active speaker timeline.
        Returns:
          clusters: List of identified face clusters
          turns: List of {"speaker_id": int, "start": float, "end": float, "crop_box": tuple}
        """
        clusters = self.discover_face_clusters(video_path)
        if not clusters:
            return [], []

        if len(clusters) == 1:
            # Single speaker across entire duration
            return clusters, [{
                "speaker_id": clusters[0]["id"],
                "start": 0.0,
                "end": duration,
                "crop_box": clusters[0]["crop_box"]
            }]

        motion_data = self.track_mouth_motion_series(video_path, clusters)
        timestamps = motion_data["timestamps"]
        motions = motion_data["motion"]

        if len(timestamps) == 0:
            return clusters, [{
                "speaker_id": clusters[0]["id"],
                "start": 0.0,
                "end": duration,
                "crop_box": clusters[0]["crop_box"]
            }]

        # Divide timeline into discrete windows of 0.8s
        window_size = 0.8
        window_starts = np.arange(0.0, duration, window_size)
        raw_turns = []

        for w_start in window_starts:
            w_end = min(duration, w_start + window_size)
            idx_mask = (timestamps >= w_start) & (timestamps < w_end)

            best_cid = clusters[0]["id"]
            best_score = -1.0
            for c in clusters:
                cid = c["id"]
                w_motion = motions[cid][idx_mask] if np.any(idx_mask) else []
                avg_m = float(np.mean(w_motion)) if len(w_motion) > 0 else 0.0
                if avg_m > best_score:
                    best_score = avg_m
                    best_cid = cid

            raw_turns.append({"speaker_id": best_cid, "start": float(w_start), "end": float(w_end)})

        # Coalesce consecutive turns with the same speaker
        merged_turns = []
        for t in raw_turns:
            if merged_turns and merged_turns[-1]["speaker_id"] == t["speaker_id"]:
                merged_turns[-1]["end"] = t["end"]
            else:
                merged_turns.append(dict(t))

        # Enforce minimum turn duration to prevent micro-flickering
        smoothed_turns = []
        for t in merged_turns:
            if not smoothed_turns:
                smoothed_turns.append(t)
            else:
                dur = t["end"] - t["start"]
                if dur < min_turn_sec and len(smoothed_turns) > 0:
                    # Absorb short burst into previous turn
                    smoothed_turns[-1]["end"] = t["end"]
                else:
                    smoothed_turns.append(t)

        # Final coalesce: merge adjacent turns with identical speaker_id
        final_turns = []
        for t in smoothed_turns:
            if final_turns and final_turns[-1]["speaker_id"] == t["speaker_id"]:
                final_turns[-1]["end"] = t["end"]
            else:
                final_turns.append(dict(t))

        # Attach crop_box to each turn
        cluster_map = {c["id"]: c["crop_box"] for c in clusters}
        for t in final_turns:
            t["crop_box"] = cluster_map.get(t["speaker_id"], clusters[0]["crop_box"])

        if final_turns:
            final_turns[0]["start"] = 0.0
            final_turns[-1]["end"] = duration

        return clusters, final_turns

    def build_dynamic_switcher_filter(
        self,
        video_path: str,
        duration: float,
        transcript_words: Optional[List[dict]] = None,
        top_h: int = DEFAULT_TOP_H,
        bottom_h: int = DEFAULT_BOTTOM_H
    ) -> Dict[str, Any]:
        """
        Builds the complete multi-speaker dynamic switcher filtergraph for FFmpeg.
        Automatically switches the top camera pane to whoever is actively talking.
        """
        clusters, turns = self.compute_speaker_turns(video_path, duration, transcript_words)

        cap = cv2.VideoCapture(video_path)
        src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
        src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        cap.release()

        # If only 1 cluster or no turns, fallback to single reactor layout
        if len(clusters) <= 1 or len(turns) <= 1:
            box = clusters[0]["crop_box"] if clusters else (int(src_w * 0.7), int(src_h * 0.05), int(src_w * 0.28), int(src_h * 0.45))
            fx, fy, fw, fh = box
            fg = (
                f"[0:v]split=2[cam_in][game_in];"
                f"[cam_in]crop={fw}:{fh}:{fx}:{fy},"
                f"scale={OUT_W}:{top_h}:flags=lanczos,setsar=1[top];"
                f"[game_in]scale={OUT_W}:{bottom_h}:force_original_aspect_ratio=increase,"
                f"crop={OUT_W}:{bottom_h},setsar=1[bottom];"
                f"[top][bottom]vstack=inputs=2[v_stacked];"
                f"[v_stacked]drawbox=y={top_h-2}:w={OUT_W}:h=4:color=#FFD700@0.8:t=fill[v_split]"
            )
            return {
                "filter_graph": fg,
                "output_label": "[v_split]",
                "caption_y": top_h + 40,
                "turns": turns,
                "clusters": clusters
            }

        # Multi-speaker dynamic switching
        # 1. Split [0:v] into: 1 for gameplay + 1 per cluster
        num_clusters = len(clusters)
        split_names = "".join(f"[c_{c['id']}_in]" for c in clusters)
        fg_lines = [f"[0:v]split={num_clusters + 1}[game_in]{split_names};"]

        # 2. Count appearances of each cluster across all turns
        appearances = {c["id"]: 0 for c in clusters}
        appearances[turns[0]["speaker_id"]] += 1
        for t in turns[1:]:
            appearances[t["speaker_id"]] += 1

        # 3. Scale each face cluster to 1080 x top_h and split for multi-turn reuse
        pad_allocations = {c["id"]: [] for c in clusters}
        for c in clusters:
            cid = c["id"]
            count = appearances[cid]
            if count == 0:
                continue
            cx, cy, cw, ch = c["crop_box"]
            if count == 1:
                fg_lines.append(
                    f"[c_{cid}_in]crop={cw}:{ch}:{cx}:{cy},"
                    f"scale={OUT_W}:{top_h}:flags=lanczos,setsar=1[face_{cid}_0];"
                )
                pad_allocations[cid].append(f"[face_{cid}_0]")
            else:
                out_splits = "".join(f"[face_{cid}_{k}]" for k in range(count))
                fg_lines.append(
                    f"[c_{cid}_in]crop={cw}:{ch}:{cx}:{cy},"
                    f"scale={OUT_W}:{top_h}:flags=lanczos,setsar=1,split={count}{out_splits};"
                )
                pad_allocations[cid] = [f"[face_{cid}_{k}]" for k in range(count)]

        # 4. Chain overlays to dynamically switch faces based on turns
        base_cid = turns[0]["speaker_id"]
        curr_top = pad_allocations[base_cid].pop(0)

        for idx, t in enumerate(turns[1:], start=1):
            next_cid = t["speaker_id"]
            next_pad = pad_allocations[next_cid].pop(0)
            start_t, end_t = t["start"], t["end"]
            next_top = f"[top_stage_{idx}]"
            enable_expr = f"between(t,{start_t:.3f},{end_t:.3f})"
            fg_lines.append(
                f"{curr_top}{next_pad}overlay=0:0:enable='{enable_expr}'{next_top};"
            )
            curr_top = next_top

        # 4. Scale gameplay to 1080 x bottom_h
        fg_lines.append(
            f"[game_in]scale={OUT_W}:{bottom_h}:force_original_aspect_ratio=increase,"
            f"crop={OUT_W}:{bottom_h},setsar=1[bottom];"
        )

        # 5. Vertical stack [active_top][bottom] + dividing accent bar
        fg_lines.append(f"{curr_top}[bottom]vstack=inputs=2[v_stacked];")
        fg_lines.append(f"[v_stacked]drawbox=y={top_h-2}:w={OUT_W}:h=4:color=#FFD700@0.8:t=fill[v_split]")

        return {
            "filter_graph": "".join(fg_lines),
            "output_label": "[v_split]",
            "caption_y": top_h + 40,
            "turns": turns,
            "clusters": clusters
        }
