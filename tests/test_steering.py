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
        hand[joint].y = y - 0.10 if extended else y + 0.15
    return hand


def make_pointing_hand(x: float, y: float):
    hand = make_gesture_hand(x, y, extended=False)
    hand[8].y = y - 0.30
    hand[6].y = y - 0.10
    return hand


def make_thumbs_up_hand(x: float, y: float):
    hand = make_gesture_hand(x, y, extended=False)
    hand[3].y = y + 0.05
    hand[4].y = y - 0.30
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


def test_both_open_hands_reverse():
    left = make_gesture_hand(0.25, 0.6, extended=True)
    right = make_gesture_hand(0.75, 0.6, extended=True)
    controls = controls_from_hands([left, right])
    assert not controls.accelerate
    assert controls.brake
    assert extended_finger_count(right) == 4


def test_both_fists_accelerate():
    left = make_gesture_hand(0.25, 0.6, extended=False)
    right = make_gesture_hand(0.75, 0.6, extended=False)
    controls = controls_from_hands([left, right])
    assert controls.accelerate
    assert not controls.drift


def test_right_fist_and_left_open_hand_drift():
    left = make_gesture_hand(0.25, 0.6, extended=True)
    right = make_gesture_hand(0.75, 0.6, extended=False)
    controls = controls_from_hands([left, right])
    assert controls.drift
    assert not controls.accelerate


def test_thumbs_up_on_one_hand_triggers_nitro():
    thumbs_up = make_thumbs_up_hand(0.75, 0.6)
    controls = controls_from_hands([thumbs_up])
    assert controls.nitro
    assert not controls.accelerate


def test_index_point_on_one_hand_triggers_shoot():
    controls = controls_from_hands([make_pointing_hand(0.75, 0.6)])
    assert controls.shoot
