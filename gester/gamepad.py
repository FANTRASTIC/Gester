from __future__ import annotations


class VirtualGamepad:
    """Send Gester steering to a virtual Xbox 360 controller."""

    def __init__(self) -> None:
        try:
            import vgamepad as vg
        except ImportError as exc:
            raise RuntimeError(
                "Gamepad output requires vgamepad. Install requirements.txt "
                "and the ViGEmBus driver."
            ) from exc

        try:
            self._gamepad = vg.VX360Gamepad()
        except Exception as exc:
            raise RuntimeError(
                "The virtual Xbox controller could not start. Install the "
                "ViGEmBus driver, then restart Gester."
            ) from exc

    def set_steering(self, value: float) -> None:
        self.set_controls(steering=value)

    def set_controls(
        self,
        *,
        steering: float = 0.0,
        accelerate: bool = False,
        brake: bool = False,
        nitro: bool = False,
        drift: bool = False,
    ) -> None:
        import vgamepad as vg

        stick_value = int(max(-1.0, min(1.0, steering)) * 32767)
        self._gamepad.left_joystick(x_value=stick_value, y_value=0)
        self._gamepad.right_trigger(value=255 if accelerate else 0)
        self._gamepad.left_trigger(value=255 if brake else 0)
        self._set_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A, nitro)
        self._set_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, drift)
        self._gamepad.update()

    def _set_button(self, button, pressed: bool) -> None:
        if pressed:
            self._gamepad.press_button(button=button)
        else:
            self._gamepad.release_button(button=button)

    def reset(self) -> None:
        self.set_controls()

    def close(self) -> None:
        self.reset()
        self._gamepad.reset()
        self._gamepad.update()