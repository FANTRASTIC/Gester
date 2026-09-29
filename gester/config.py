from dataclasses import dataclass


@dataclass(slots=True)
class SteeringConfig:
    """Tunable steering settings for the first Gester prototype."""

    max_angle_degrees: float = 40.0
    deadzone: float = 0.08
    smoothing_alpha: float = 0.25


@dataclass(slots=True)
class CameraConfig:
    index: int = 0
    width: int = 1280
    height: int = 720
