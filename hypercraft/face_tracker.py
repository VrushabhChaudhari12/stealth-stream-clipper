"""
Face Tracking & Active Speaker Centering Engine.
Extracted and optimized from supoclip YuNet ONNX pipeline with Haar cascade fallback.
Enables instant streamer facecam isolation, auto-centering, and reaction split-screens.
"""

from pathlib import Path
from typing import List, Optional, Sequence, Tuple
import cv2
import numpy as np

MODEL_PATH = Path(__file__).parent / "models" / "face_detection_yunet_2023mar.onnx"
FaceBox = Tuple[float, float, float, float, float]  # (x, y, w, h, score)
Box = Tuple[float, float, float, float]
FaceFrame = Tuple[float, Sequence[Box]]


class FaceTracker:
    def __init__(self, score_threshold: float = 0.6, nms_threshold: float = 0.3):
        self.detector = None
        self.has_yunet = False
        if MODEL_PATH.is_file() and hasattr(cv2, "FaceDetectorYN"):
            try:
                self.detector = cv2.FaceDetectorYN.create(
                    str(MODEL_PATH), "", (320, 320), score_threshold, nms_threshold, 50
                )
                self.has_yunet = True
                self.input_size = None
            except Exception as e:
                print(f"[FaceTracker] YuNet initialization failed: {e}. Falling back to Haar.")

        if not self.has_yunet:
            # Haar Cascade fallback
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect(self, frame_bgr: np.ndarray, max_width: int = 960) -> List[FaceBox]:
        """Detect faces returning (x, y, w, h, score) in original pixel coordinates."""
        h, w = frame_bgr.shape[:2]
        if w <= 0 or h <= 0:
            return []

        scale = 1.0
        img = frame_bgr
        if w > max_width:
            scale = max_width / float(w)
            img = cv2.resize(frame_bgr, (max_width, max(1, int(round(h * scale)))), interpolation=cv2.INTER_AREA)

        if self.has_yunet and self.detector is not None:
            sz = (img.shape[1], img.shape[0])
            if sz != self.input_size:
                self.detector.setInputSize(sz)
                self.input_size = sz

            _, faces = self.detector.detect(np.ascontiguousarray(img))
            if faces is None:
                return []
            boxes = []
            for face in faces:
                x, y, fw, fh = (float(v) / scale for v in face[:4])
                score = float(face[-1])
                x0, y0 = max(0.0, x), max(0.0, y)
                x1, y1 = min(float(w), x + fw), min(float(h), y + fh)
                if x1 - x0 > 2 and y1 - y0 > 2:
                    boxes.append((x0, y0, x1 - x0, y1 - y0, score))
            return boxes
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            boxes = []
            for (x, y, fw, fh) in faces:
                x_orig, y_orig = float(x) / scale, float(y) / scale
                w_orig, h_orig = float(fw) / scale, float(fh) / scale
                boxes.append((x_orig, y_orig, w_orig, h_orig, 0.9))
            return boxes

    def sample_video_faces(self, video_path: str, num_samples: int = 15) -> Sequence[FaceFrame]:
        """Sample faces at uniform intervals across video."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0.0

        if duration <= 0 or total_frames <= 0:
            cap.release()
            return []

        timestamps = np.linspace(0.2, max(0.2, duration - 0.5), min(num_samples, max(3, int(duration * 2))))
        samples = []
        for t in timestamps:
            cap.set(cv2.CAP_PROP_POS_MSEC, float(t) * 1000.0)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            detected = self.detect(frame)
            boxes = [(x, y, w, h) for (x, y, w, h, s) in detected]
            samples.append((float(t), boxes))

        cap.release()
        return samples

    def find_reactor_face(self, width: int, height: int, samples: Sequence[FaceFrame]) -> Optional[Box]:
        """Find a stable webcam reaction face (typically top or corner quadrant)."""
        if len(samples) < 3:
            return None

        # Check corners or quadrants: Right vs Left
        for right in (True, False):
            found = []
            for _, faces in samples:
                # Look for faces in left or right side, upper 40% of frame
                corner = [
                    f for f in faces
                    if (f[0] + f[2] / 2 > width * 0.60 if right else f[0] + f[2] / 2 < width * 0.40)
                    and f[1] + f[3] / 2 < height * 0.65
                    and 0.001 < (f[2] * f[3]) / (width * height) < 0.25
                ]
                if len(corner) >= 1:
                    # Pick dominant face in the corner
                    dom = max(corner, key=lambda f: f[2] * f[3])
                    found.append(dom)

            if len(found) >= max(2, len(samples) * 0.4):
                boxes = np.asarray(found)
                centres = boxes[:, :2] + boxes[:, 2:] / 2
                # Check positional stability
                if np.std(centres[:, 0]) < width * 0.06 and np.std(centres[:, 1]) < height * 0.06:
                    return tuple(float(v) for v in np.median(boxes, axis=0))

        # Check full upper half if corner check didn't match
        all_upper = []
        for _, faces in samples:
            for f in faces:
                if f[1] + f[3] / 2 < height * 0.5 and (f[2] * f[3]) / (width * height) > 0.01:
                    all_upper.append(f)
        if len(all_upper) >= max(2, len(samples) * 0.5):
            boxes = np.asarray(all_upper)
            return tuple(float(v) for v in np.median(boxes, axis=0))

        return None
