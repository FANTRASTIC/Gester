from __future__ import annotations

from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Standard MediaPipe 21-point hand skeleton.
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)


class HandTracker:
    """MediaPipe Hand Landmarker wrapper configured for video frames."""

    def __init__(self, model_path: str | Path) -> None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Hand model not found: {model_path}\n"
                "Run: python setup_model.py"
            )

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55,
        )
        self._detector = vision.HandLandmarker.create_from_options(options)

    def detect(self, bgr_frame, timestamp_ms: int):
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self._detector.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        self._detector.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def draw_hand(frame, landmarks) -> None:
    height, width = frame.shape[:2]

    points: list[tuple[int, int]] = []
    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        points.append((x, y))

    for start, end in HAND_CONNECTIONS:
        cv2.line(frame, points[start], points[end], (220, 220, 220), 2, cv2.LINE_AA)

    for point in points:
        cv2.circle(frame, point, 4, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, point, 6, (0, 0, 0), 1, cv2.LINE_AA)
