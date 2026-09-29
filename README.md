# Gester v0.1

Gester is a Python computer-vision prototype that turns two hands in front of a webcam into virtual Xbox controller input for racing games.

The current milestone supports steering, acceleration, braking, nitro, and drift/skid input:

`webcam -> MediaPipe hand landmarks -> gestures -> virtual Xbox controller -> game`

## What v0.1 does

- Opens your webcam with OpenCV.
- Mirrors the video so interaction feels natural.
- Detects up to two hands with MediaPipe Hand Landmarker.
- Draws the 21 landmarks of each detected hand.
- Estimates a palm center from the wrist and MCP knuckles.
- Treats the two palm centers as the ends of an imaginary steering wheel.
- Calculates wheel rotation in degrees.
- Converts it to a `-1.0 .. +1.0` steering signal.
- Applies a center dead zone and exponential smoothing.
- Immediately returns to neutral if two hands are not visible.
- Sends steering to the virtual Xbox left-stick X axis.
- Sends acceleration and braking to the right and left triggers.
- Sends nitro to Xbox A and drift/skid to Xbox Left Shoulder.
- Shows FPS and steering information in a live HUD.

## Recommended environment

Windows 10/11 and Python 3.11-3.13 are good choices for the project. A normal built-in or USB webcam is enough.

## Setup (Windows PowerShell)

From inside this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_model.py
python main.py
```

The virtual controller also requires the **ViGEmBus** driver on Windows. If it
is unavailable, Gester continues in display-only mode.

If PowerShell blocks virtual-environment activation, you can use Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python setup_model.py
python main.py
```

## How to use it

1. Put the webcam roughly centered in front of you.
2. Hold both hands up as if gripping an invisible steering wheel.
3. Keep the palms separated horizontally.
4. Rotate the imaginary wheel clockwise/right or counterclockwise/left.
5. Watch `ANGLE` and `STEERING` in the upper-left HUD.
6. Press **Q** or **Esc** to quit.

## Gesture controls

The preview is mirrored. Keep both palms separated horizontally:

| Gesture | Virtual Xbox input |
| --- | --- |
| Rotate both hands like a wheel | Left stick X: steering |
| Open hand on screen-right | Right trigger: accelerate |
| Open hand on screen-left | Left trigger: brake/reverse |
| Fist on screen-right | A button: nitro |
| Fist on screen-left | Left Shoulder: drift/skid |

The separate **Gester Controls** window also lists the planned gestures for
fire, look back, rescue, and pause. Those four gestures are displayed for the
next control milestone but are not active yet.

For SuperTuxKart, open the controller settings and bind steering, accelerate,
brake/reverse, nitro, and skid to those virtual Xbox inputs.

Expected output:

- Straight hands: steering near `0.000`.
- Clockwise tilt: positive steering toward `+1.000`.
- Counterclockwise tilt: negative steering toward `-1.000`.

## Tuning

Full steering currently occurs at 40 degrees:

```powershell
python main.py --max-angle 40
```

More sensitive:

```powershell
python main.py --max-angle 25
```

Less sensitive:

```powershell
python main.py --max-angle 55
```

Change the center dead zone:

```powershell
python main.py --deadzone 0.10
```

Change smoothing. Smaller values feel smoother/slower; larger values react faster:

```powershell
python main.py --smoothing 0.20
```

If the wrong webcam opens:

```powershell
python main.py --camera 1
```

## Run tests

```powershell
pytest -q
```

The tests cover the steering mathematics independently of the webcam and MediaPipe.

## Project structure

```text
Gester_v0_1/
├── main.py
├── setup_model.py
├── requirements.txt
├── models/
├── gester/
│   ├── config.py
│   ├── tracking.py
│   ├── steering.py
│   ├── gestures.py
│   ├── gamepad.py
│   └── overlay.py
└── tests/
    └── test_steering.py
```

The important architecture is:

```text
Camera
  -> HandTracker
  -> Gesture/Steering Engine
  -> VehicleState
  -> Output Adapter
       -> Debug
       -> Keyboard
      -> Virtual Xbox controller
```

That keeps game compatibility separate from computer vision.
