from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees
from typing import Sequence

from .config import SteeringConfig


@dataclass(slots=True, frozen=True)
class Point:
    x: float
    y: float


@dataclass(slots=True, frozen=True)
class SteeringReading:
    angle_degrees: float
    raw_value: float
    value: float
    left_center: Point
    right_center: Point


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def palm_center(landmarks: Sequence[object]) -> Point:
    """Return a stable palm center from MediaPipe's 21 hand landmarks.

    The wrist and four MCP knuckles are averaged. Each landmark object only
    needs x and y attributes, which also makes this function easy to test.
    """

    indices = (0, 5, 9, 13, 17)
    if len(landmarks) < 21:
        raise ValueError("Expected 21 hand landmarks.")

    x = sum(float(landmarks[i].x) for i in indices) / len(indices)
    y = sum(float(landmarks[i].y) for i in indices) / len(indices)
    return Point(x=x, y=y)


def wheel_angle(left_center: Point, right_center: Point) -> float:
    """Angle of the imaginary wheel in degrees.

    Frames are mirrored before tracking. Image y grows downward, so a
    clockwise/right turn naturally produces a positive angle.
    """

    dx = right_center.x - left_center.x
    dy = right_center.y - left_center.y
    return degrees(atan2(dy, dx))


def normalize_angle(angle_degrees: float, max_angle_degrees: float) -> float:
    if max_angle_degrees <= 0:
        raise ValueError("max_angle_degrees must be positive.")
    return clamp(angle_degrees / max_angle_degrees, -1.0, 1.0)


def apply_deadzone(value: float, deadzone: float) -> float:
    """Apply a rescaled center dead zone while preserving the full range."""

    deadzone = clamp(deadzone, 0.0, 0.95)
    if abs(value) <= deadzone:
        return 0.0

    magnitude = (abs(value) - deadzone) / (1.0 - deadzone)
    return clamp(magnitude, 0.0, 1.0) * (1.0 if value > 0 else -1.0)


class SteeringSmoother:
    def __init__(self, alpha: float = 0.25) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in the interval (0, 1].")
        self.alpha = alpha
        self._value: float | None = None

    def update(self, target: float) -> float:
        if self._value is None:
            self._value = target
        else:
            self._value = self.alpha * target + (1.0 - self.alpha) * self._value
        return self._value

    def reset(self) -> None:
        self._value = None


class SteeringEngine:
    def __init__(self, config: SteeringConfig | None = None) -> None:
        self.config = config or SteeringConfig()
        self.smoother = SteeringSmoother(self.config.smoothing_alpha)

    def calculate(self, hand_a: Sequence[object], hand_b: Sequence[object]) -> SteeringReading:
        center_a = palm_center(hand_a)
        center_b = palm_center(hand_b)

        # Screen position is more useful than anatomical handedness here:
        # we only care which palm is currently on the left/right end of the
        # imaginary steering wheel.
        left_center, right_center = sorted((center_a, center_b), key=lambda p: p.x)

        angle = wheel_angle(left_center, right_center)
        raw = normalize_angle(angle, self.config.max_angle_degrees)
        deadzoned = apply_deadzone(raw, self.config.deadzone)
        smoothed = self.smoother.update(deadzoned)

        return SteeringReading(
            angle_degrees=angle,
            raw_value=raw,
            value=clamp(smoothed, -1.0, 1.0),
            left_center=left_center,
            right_center=right_center,
        )

    def reset(self) -> None:
        self.smoother.reset()
