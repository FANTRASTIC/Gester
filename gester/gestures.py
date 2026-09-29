from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Sequence

from .steering import Point, palm_center


@dataclass(slots=True, frozen=True)
class GestureState:
    accelerate: bool = False
    brake: bool = False
    nitro: bool = False
    drift: bool = False


def extended_finger_count(landmarks: Sequence[object]) -> int:
    """Count extended fingers using distances from the wrist.

    Distance-based detection works when the hand is tilted, unlike a simple
    image-y comparison. The thumb is intentionally excluded because its pose
    varies substantially with the steering-wheel grip.
    """

    if len(landmarks) < 21:
        raise ValueError("Expected 21 hand landmarks.")

    wrist = landmarks[0]
    pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
    return sum(
        hypot(landmarks[tip].x - wrist.x, landmarks[tip].y - wrist.y)
        > hypot(landmarks[joint].x - wrist.x, landmarks[joint].y - wrist.y) * 1.15
        for tip, joint in pairs
    )


def is_open_hand(landmarks: Sequence[object]) -> bool:
    return extended_finger_count(landmarks) >= 2


def is_fist(landmarks: Sequence[object]) -> bool:
    return extended_finger_count(landmarks) == 0


def controls_from_hands(
    hand_a: Sequence[object], hand_b: Sequence[object]
) -> GestureState:
    """Map screen-left and screen-right hands to driving controls.

    The preview is mirrored, so screen-right is the user's right-hand side.
    Open right hand accelerates; open left hand brakes. Fists trigger nitro
    on the right and drift/skid on the left.
    """

    first_center = palm_center(hand_a)
    second_center = palm_center(hand_b)
    left_hand, right_hand = sorted(
        ((first_center, hand_a), (second_center, hand_b)),
        key=lambda item: item[0].x,
    )

    _, left_landmarks = left_hand
    _, right_landmarks = right_hand
    return GestureState(
        accelerate=is_open_hand(right_landmarks),
        brake=is_open_hand(left_landmarks),
        nitro=is_fist(right_landmarks),
        drift=is_fist(left_landmarks),
    )