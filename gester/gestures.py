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
    shoot: bool = False


def _finger_is_extended(landmarks: Sequence[object], tip: int, joint: int) -> bool:
    wrist = landmarks[0]
    return hypot(landmarks[tip].x - wrist.x, landmarks[tip].y - wrist.y) > (
        hypot(landmarks[joint].x - wrist.x, landmarks[joint].y - wrist.y) * 1.15
    )


def extended_finger_count(landmarks: Sequence[object]) -> int:
    """Count extended fingers using distances from the wrist.

    Distance-based detection works when the hand is tilted, unlike a simple
    image-y comparison. The thumb is intentionally excluded because its pose
    varies substantially with the steering-wheel grip.
    """

    if len(landmarks) < 21:
        raise ValueError("Expected 21 hand landmarks.")

    pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
    return sum(_finger_is_extended(landmarks, tip, joint) for tip, joint in pairs)


def is_open_hand(landmarks: Sequence[object]) -> bool:
    return extended_finger_count(landmarks) >= 2


def is_fist(landmarks: Sequence[object]) -> bool:
    return extended_finger_count(landmarks) == 0 and not is_thumbs_up(landmarks)


def is_thumbs_up(landmarks: Sequence[object]) -> bool:
    """Detect an upward-pointing thumb while the four fingers are curled."""

    if len(landmarks) < 21 or extended_finger_count(landmarks) != 0:
        return False
    thumb_ip = landmarks[3]
    thumb_tip = landmarks[4]
    return (
        _finger_is_extended(landmarks, 4, 3)
        and thumb_tip.y < thumb_ip.y
    )


def is_pointing(landmarks: Sequence[object]) -> bool:
    """Detect an index finger extended by itself."""

    if len(landmarks) < 21 or extended_finger_count(landmarks) != 1:
        return False
    return _finger_is_extended(landmarks, 8, 6)


def controls_from_hands(hands: Sequence[Sequence[object]]) -> GestureState:
    """Map the visible hand poses to keyboard driving actions.

    Two fists accelerate; two open palms reverse. A right fist with a left
    open palm drifts. Thumbs-up and index-pointing work with either hand.
    """

    if not hands:
        return GestureState()

    ordered_hands = sorted(hands, key=lambda hand: palm_center(hand).x)
    left_hand = ordered_hands[0]
    right_hand = ordered_hands[-1]
    both_hands_visible = len(ordered_hands) >= 2

    return GestureState(
        accelerate=(
            both_hands_visible
            and is_fist(left_hand)
            and is_fist(right_hand)
        ),
        brake=(
            both_hands_visible
            and is_open_hand(left_hand)
            and is_open_hand(right_hand)
        ),
        nitro=any(is_thumbs_up(hand) for hand in ordered_hands),
        drift=(
            both_hands_visible
            and is_open_hand(left_hand)
            and is_fist(right_hand)
        ),
        shoot=any(is_pointing(hand) for hand in ordered_hands),
    )
