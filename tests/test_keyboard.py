from types import SimpleNamespace

from gester.keyboard import KeyboardController


def test_keyboard_controller_holds_and_releases_changed_keys(monkeypatch):
    events = []
    fake_keyboard = SimpleNamespace(
        PAUSE=0,
        keyDown=lambda key: events.append(("down", key)),
        keyUp=lambda key: events.append(("up", key)),
    )
    monkeypatch.setitem(__import__("sys").modules, "pydirectinput", fake_keyboard)

    controller = KeyboardController()
    controller.set_controls(steering=0.5, accelerate=True)
    controller.set_controls(steering=-0.5, brake=True)
    controller.close()

    assert set(events[:2]) == {("down", "d"), ("down", "w")}
    assert set(events[2:4]) == {("up", "d"), ("up", "w")}
    assert set(events[4:6]) == {("down", "a"), ("down", "s")}
    assert set(events[6:8]) == {("up", "a"), ("up", "s")}