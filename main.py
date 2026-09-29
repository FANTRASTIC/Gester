from __future__ import annotations

import argparse
import platform
import time
from pathlib import Path

import cv2

from gester.config import CameraConfig, SteeringConfig
from gester.gamepad import VirtualGamepad
from gester.gestures import controls_from_hands
from gester.overlay import draw_controls_legend, draw_hud, draw_steering
from gester.steering import SteeringEngine
from gester.tracking import HandTracker, draw_hand


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = ROOT / "models" / "hand_landmarker.task"


def open_camera(config: CameraConfig):
    # DirectShow usually gives predictable webcam startup on Windows. Other
    # platforms use OpenCV's default backend.
    if platform.system() == "Windows":
        camera = cv2.VideoCapture(config.index, cv2.CAP_DSHOW)
        if not camera.isOpened():
            camera.release()
            camera = cv2.VideoCapture(config.index)
    else:
        camera = cv2.VideoCapture(config.index)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
    return camera


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gester v0.1 - webcam steering prototype")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0)")
    parser.add_argument("--max-angle", type=float, default=40.0, help="Degrees that equal full steering lock")
    parser.add_argument("--deadzone", type=float, default=0.08, help="Center steering deadzone, 0 to 0.95")
    parser.add_argument("--smoothing", type=float, default=0.25, help="EMA alpha, 0 < value <= 1")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    camera_config = CameraConfig(index=args.camera)
    steering_config = SteeringConfig(
        max_angle_degrees=args.max_angle,
        deadzone=args.deadzone,
        smoothing_alpha=args.smoothing,
    )

    camera = open_camera(camera_config)
    if not camera.isOpened():
        print("ERROR: Could not open the webcam.")
        print("Try another device index, for example: python main.py --camera 1")
        return 1

    engine = SteeringEngine(steering_config)
    try:
        gamepad = VirtualGamepad()
    except RuntimeError as error:
        print(f"WARNING: {error}")
        print("Continuing in display-only mode.")
        gamepad = None

    previous_time = time.perf_counter()
    fps = 0.0
    last_timestamp_ms = -1

    print("Gester v0.1 running.")
    print("Hold both hands as if you are gripping an imaginary steering wheel.")
    print("Press Q or ESC to quit.")

    try:
        with HandTracker(DEFAULT_MODEL) as tracker:
            while True:
                ok, frame = camera.read()
                if not ok or frame is None:
                    print("ERROR: Failed to read a camera frame.")
                    break

                # Mirror the image so interaction feels like looking in a mirror.
                frame = cv2.flip(frame, 1)

                timestamp_ms = int(time.monotonic() * 1000)
                if timestamp_ms <= last_timestamp_ms:
                    timestamp_ms = last_timestamp_ms + 1
                last_timestamp_ms = timestamp_ms

                result = tracker.detect(frame, timestamp_ms)
                hands = result.hand_landmarks

                for hand in hands:
                    draw_hand(frame, hand)

                reading = None
                gesture_text = "SHOW BOTH HANDS"
                if len(hands) >= 2:
                    reading = engine.calculate(hands[0], hands[1])
                    gestures = controls_from_hands(hands[0], hands[1])
                    gesture_names = []
                    if gestures.accelerate:
                        gesture_names.append("ACCEL")
                    if gestures.brake:
                        gesture_names.append("BRAKE")
                    if gestures.nitro:
                        gesture_names.append("NITRO")
                    if gestures.drift:
                        gesture_names.append("DRIFT")
                    gesture_text = "GESTURE: " + (" + ".join(gesture_names) if gesture_names else "NONE")
                    if gamepad is not None:
                        gamepad.set_controls(
                            steering=reading.value,
                            accelerate=gestures.accelerate,
                            brake=gestures.brake,
                            nitro=gestures.nitro,
                            drift=gestures.drift,
                        )
                    draw_steering(frame, reading)
                else:
                    # Safety behavior: no reliable two-hand steering means neutral.
                    engine.reset()
                    if gamepad is not None:
                        gamepad.reset()

                now = time.perf_counter()
                instantaneous_fps = 1.0 / max(now - previous_time, 1e-6)
                previous_time = now
                fps = instantaneous_fps if fps == 0.0 else (0.1 * instantaneous_fps + 0.9 * fps)

                draw_hud(frame, hand_count=len(hands), fps=fps, reading=reading)
                draw_controls_legend(frame, gesture_text=gesture_text)
                cv2.imshow("Gester v0.1 - Steering Prototype", frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q"), 27):
                    break
                if cv2.getWindowProperty(
                    "Gester v0.1 - Steering Prototype",
                    cv2.WND_PROP_VISIBLE,
                ) < 1:
                    break
    finally:
        if gamepad is not None:
            gamepad.close()
        camera.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
