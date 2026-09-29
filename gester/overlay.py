from __future__ import annotations

import cv2
import numpy as np

from .steering import Point, SteeringReading


def _pixel(point: Point, frame) -> tuple[int, int]:
    height, width = frame.shape[:2]
    return int(point.x * width), int(point.y * height)


def draw_steering(frame, reading: SteeringReading) -> None:
    left = _pixel(reading.left_center, frame)
    right = _pixel(reading.right_center, frame)

    cv2.line(frame, left, right, (255, 255, 255), 4, cv2.LINE_AA)
    cv2.circle(frame, left, 10, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(frame, right, 10, (255, 255, 255), -1, cv2.LINE_AA)


def draw_hud(frame, *, hand_count: int, fps: float, reading: SteeringReading | None) -> None:
    cv2.rectangle(frame, (18, 18), (430, 185), (0, 0, 0), -1)

    lines = [
        f"HANDS: {hand_count}/2",
        f"FPS: {fps:5.1f}",
    ]

    if reading is None:
        lines.extend([
            "ANGLE: --",
            "STEERING: 0.000",
            "STATUS: SHOW BOTH HANDS",
        ])
    else:
        direction = "RIGHT" if reading.value > 0.03 else "LEFT" if reading.value < -0.03 else "CENTER"
        lines.extend([
            f"ANGLE: {reading.angle_degrees:+6.1f} deg",
            f"STEERING: {reading.value:+.3f}",
            f"STATUS: {direction}",
        ])

    for index, text in enumerate(lines):
        cv2.putText(
            frame,
            text,
            (34, 48 + index * 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.68,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    height, width = frame.shape[:2]
    center_x = width // 2
    meter_y = height - 48
    meter_half_width = min(300, width // 3)
    cv2.line(frame, (center_x - meter_half_width, meter_y), (center_x + meter_half_width, meter_y), (255, 255, 255), 2)
    cv2.line(frame, (center_x, meter_y - 12), (center_x, meter_y + 12), (255, 255, 255), 2)

    steering = 0.0 if reading is None else reading.value
    marker_x = int(center_x + steering * meter_half_width)
    cv2.circle(frame, (marker_x, meter_y), 10, (255, 255, 255), -1)

    cv2.putText(frame, "LEFT", (center_x - meter_half_width, meter_y - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(frame, "RIGHT", (center_x + meter_half_width - 48, meter_y - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)


def draw_controls_legend(frame, *, gesture_text: str = "") -> None:
    """Display the gesture mapping in the lower-left camera area."""

    height, width = frame.shape[:2]
    panel_left = 18
    panel_bottom = height - 18
    panel_top = max(190, height - 250)
    panel_right = min(width - 18, 560)
    cv2.rectangle(
        frame,
        (panel_left, panel_top),
        (panel_right, panel_bottom),
        (0, 0, 0),
        -1,
    )

    lines = (
        "KEYBOARD CONTROLS",
        "Rotate hands: A/D steer",
        "Both fists: W accelerate",
        "Both palms open: S reverse",
        "Right fist + left open: SPACE drift",
        "Thumbs-up: SHIFT nitro",
        "Index point: CTRL shoot",
    )
    for index, text in enumerate(lines):
        cv2.putText(
            frame,
            text,
            (34, panel_top + 32 + index * 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62 if index else 0.72,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    if gesture_text:
        cv2.putText(
            frame,
            gesture_text,
            (34, panel_top - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.78,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )


def draw_controls_window() -> None:
    """Show the complete gesture map in a separate, resizable window."""

    canvas = np.zeros((470, 820, 3), dtype=np.uint8)
    canvas[:] = (24, 24, 24)
    lines = (
        ("GESTER KEYBOARD CONTROLS", 0.95, 2, (255, 255, 255)),
        ("Rotate hands: A/D steering", 0.62, 1, (255, 255, 255)),
        ("Both fists: W accelerate", 0.62, 1, (255, 255, 255)),
        ("Both palms open: S reverse", 0.62, 1, (255, 255, 255)),
        ("Right fist + left open: SPACE drift", 0.62, 1, (255, 255, 255)),
        ("Thumbs-up, either hand: SHIFT nitro", 0.62, 1, (255, 255, 255)),
        ("Index point, either hand: CTRL shoot", 0.62, 1, (255, 255, 255)),
        ("Keep the game window focused for input.", 0.56, 1, (190, 190, 190)),
    )
    for index, (text, scale, thickness, color) in enumerate(lines):
        cv2.putText(
            canvas,
            text,
            (28, 38 + index * 29),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

    cv2.namedWindow("Gester Controls", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Gester Controls", 820, 470)
    cv2.imshow("Gester Controls", canvas)
