from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "hand_landmarker.task"


def main() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        print(f"Model already exists: {MODEL_PATH}")
        return

    print("Downloading MediaPipe Hand Landmarker model...")
    try:
        with urlopen(MODEL_URL, timeout=60) as response, MODEL_PATH.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
    except Exception:
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        raise

    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
