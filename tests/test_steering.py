from dataclasses import dataclass

import pytest

from gester.steering import (
    Point,
    SteeringSmoother,
    apply_deadzone,
    normalize_angle,
    palm_center,
    wheel_angle,
)
from gester.gestures import controls_from_hands, extended_finger_count


@dataclass
class Landmark:
    x: float
    y: float


def make_hand(x: float, y: float):
    return [Landmark(x, y) for _ in range(21)]


def make_gesture_hand(x: float, y: float, extended: bool):
    hand = make_hand(x, y)
    for tip, joint in ((8, 6), (12, 10), (16, 14), (20, 18)):
        hand[tip].y = y - 0.30 if extended else y + 0.05
        hand[joint].y = y - 0.10 if extended else y
    return hand


def test_palm_center():
    hand = make_hand(0.25, 0.75)
    center = palm_center(hand)
    assert center == Point(0.25, 0.75)


def test_straight_wheel_is_zero_degrees():
    assert wheel_angle(Point(0.2, 0.5), Point(0.8, 0.5)) == pytest.approx(0.0)


def test_clockwise_tilt_is_positive():
    assert wheel_angle(Point(0.2, 0.4), Point(0.8, 0.6)) > 0


def test_angle_normalization_clamps():
    assert normalize_angle(20, 40) == pytest.approx(0.5)
    assert normalize_angle(100, 40) == pytest.approx(1.0)
    assert normalize_angle(-100, 40) == pytest.approx(-1.0)


def test_deadzone_centers_small_input():
    assert apply_deadzone(0.05, 0.08) == 0.0
    assert apply_deadzone(-0.05, 0.08) == 0.0
    assert apply_deadzone(1.0, 0.08) == pytest.approx(1.0)


def test_smoother_moves_toward_target():
    smoother = SteeringSmoother(alpha=0.25)
    assert smoother.update(0.0) == pytest.approx(0.0)
    assert smoother.update(1.0) == pytest.approx(0.25)


def test_open_right_hand_accelerates_and_open_left_hand_brakes():
    left = make_gesture_hand(0.25, 0.6, extended=True)
    right = make_gesture_hand(0.75, 0.6, extended=True)
    controls = controls_from_hands(left, right)
    assert controls.accelerate
    assert controls.brake
    assert extended_finger_count(right) == 4


def test_fists_trigger_nitro_and_drift_by_screen_side():
    left = make_gesture_hand(0.25, 0.6, extended=False)
    right = make_gesture_hand(0.75, 0.6, extended=False)
    controls = controls_from_hands(left, right)
    assert controls.nitro
    assert controls.drift
