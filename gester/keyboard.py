from __future__ import annotations


class KeyboardController:
    """Send gesture actions as held keys to the currently focused application."""

    steering_threshold = 0.12

    def __init__(self) -> None:
        try:
            import pydirectinput
        except ImportError as exc:
            raise RuntimeError(
                "Keyboard output requires PyDirectInput. Install requirements.txt."
            ) from exc

        self._keyboard = pydirectinput
        self._held_keys: set[str] = set()
        self._keyboard.PAUSE = 0

    def set_controls(
        self,
        *,
        steering: float = 0.0,
        accelerate: bool = False,
        brake: bool = False,
        nitro: bool = False,
        drift: bool = False,
        shoot: bool = False,
    ) -> None:
        desired_keys = set()
        if steering <= -self.steering_threshold:
            desired_keys.add("a")
        elif steering >= self.steering_threshold:
            desired_keys.add("d")
        if accelerate:
            desired_keys.add("w")
        if brake:
            desired_keys.add("s")
        if drift:
            desired_keys.add("space")
        if nitro:
            desired_keys.add("shift")
        if shoot:
            desired_keys.add("ctrl")

        for key in self._held_keys - desired_keys:
            self._keyboard.keyUp(key)
        for key in desired_keys - self._held_keys:
            self._keyboard.keyDown(key)
        self._held_keys = desired_keys

    def reset(self) -> None:
        self.set_controls()

    def close(self) -> None:
        self.reset()