"""Platform input adapter."""

import importlib
import logging
import math
import shutil
import subprocess
import time

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

WINDOWS_WHEEL_DELTA = 120
LINUX_CLICK_SOURCE_WIDTH = 3840
LINUX_CLICK_SOURCE_HEIGHT = 2160
LINUX_CLICK_TARGET_WIDTH = 1920
LINUX_CLICK_TARGET_HEIGHT = 1080

_YDOTOOL_KEYS = {
    "left": 105,
    "leftshift": 42,
    "right": 106,
    "up": 103,
    "down": 108,
    "enter": 28,
    "esc": 1,
    "escape": 1,
    "f2": 60,
    "space": 57,
    "b": 48,
    "q": 16,
    "x": 45,
    "3": 4,
}


def _windows_delta_to_wheel_ticks(scroll_amount: int) -> int:
    """Convert Windows wheel delta units to Linux wheel detents."""
    if scroll_amount == 0:
        return 0

    direction = 1 if scroll_amount > 0 else -1
    tick_count = max(1, math.floor(abs(scroll_amount) / WINDOWS_WHEEL_DELTA + 0.5))
    return direction * tick_count


def _scale_linux_click_coordinates(x: int, y: int) -> tuple[int, int]:
    """Scale 4K coordinates to the Linux screenshot size."""
    return (
        round(x * LINUX_CLICK_TARGET_WIDTH / LINUX_CLICK_SOURCE_WIDTH),
        round(y * LINUX_CLICK_TARGET_HEIGHT / LINUX_CLICK_SOURCE_HEIGHT),
    )


class _WindowsInputBackend:
    def __init__(self, controller: "KeyboardMouseDriver") -> None:
        self._pydirectinput = importlib.import_module("pydirectinput")
        setattr(self._pydirectinput, "FAILSAFE", controller.FAILSAFE)

    def press(self, key: str) -> None:
        self._pydirectinput.press(key)

    def key_down(self, key: str) -> None:
        self._pydirectinput.keyDown(key)

    def key_up(self, key: str) -> None:
        self._pydirectinput.keyUp(key)

    def hotkey(self, *keys: str) -> None:
        self._pydirectinput.hotkey(*keys)

    def move_mouse(self, x: int, y: int) -> None:
        self._pydirectinput.moveTo(x=x, y=y)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None and y is not None:
            self.move_mouse(x, y)
            self._pydirectinput.click()
            return
        self._pydirectinput.click(x=x, y=y)

    def scroll(self, scroll_amount: int) -> None:
        import pyautogui as gui

        gui.vscroll(scroll_amount)


class _YdotoolInputBackend:
    def __init__(self) -> None:
        ydotool = shutil.which("ydotool")
        if ydotool is None:
            raise RuntimeError("Linux input requires `ydotool` on PATH")
        self._ydotool = ydotool

    def _keycode(self, key: str) -> int:
        normalized_key = key.lower()
        try:
            return _YDOTOOL_KEYS[normalized_key]
        except KeyError as exc:
            supported = ", ".join(sorted(_YDOTOOL_KEYS))
            raise RuntimeError(
                f"Unsupported ydotool key `{key}`; supported: {supported}"
            ) from exc

    def _run(self, *args: str) -> None:
        subprocess.run(
            [self._ydotool, *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def press(self, key: str) -> None:
        self.key_down(key)
        self.key_up(key)

    def key_down(self, key: str) -> None:
        self._run("key", f"{self._keycode(key)}:1")

    def key_up(self, key: str) -> None:
        self._run("key", f"{self._keycode(key)}:0")

    def hotkey(self, *keys: str) -> None:
        for key in keys:
            self.key_down(key)
        for key in reversed(keys):
            self.key_up(key)

    def move_mouse(self, x: int, y: int) -> None:
        scaled_x, scaled_y = _scale_linux_click_coordinates(x, y)
        self._run("mousemove", "--absolute", "0", "0")
        time.sleep(0.1)
        self._run("mousemove", str(scaled_x), str(scaled_y))

    def click(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None and y is not None:
            self.move_mouse(x, y)
        self._run("click", "0xC0")

    def scroll(self, scroll_amount: int) -> None:
        """Scroll using existing Windows-style wheel delta units."""
        wheel_ticks = _windows_delta_to_wheel_ticks(scroll_amount)
        if wheel_ticks == 0:
            return
        self._run("mousemove", "--wheel", "-x", "0", "-y", str(wheel_ticks))


class KeyboardMouseDriver:
    """Keyboard and mouse input controller with Windows and Linux backends."""

    FAILSAFE: bool

    def __init__(self) -> None:
        self.FAILSAFE = False
        self._backend = self._create_backend()

    def _create_backend(self):
        if is_windows():
            return _WindowsInputBackend(self)
        if is_linux():
            return _YdotoolInputBackend()
        raise RuntimeError("Input is only supported on Windows and Linux")

    def press(self, key: str) -> None:
        """Press and release a key."""
        self._backend.press(key)

    def key_down(self, key: str) -> None:
        """Press and hold a key."""
        self._backend.key_down(key)

    def key_up(self, key: str) -> None:
        """Release a key."""
        self._backend.key_up(key)

    def hotkey(self, *keys: str) -> None:
        """Press a key chord."""
        self._backend.hotkey(*keys)

    def move_mouse(self, x: int, y: int) -> None:
        """Move the mouse pointer without clicking."""
        self._backend.move_mouse(x, y)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Click the primary mouse button."""
        self._backend.click(x=x, y=y)

    def scroll(self, scroll_amount: int) -> None:
        """Scroll the mouse wheel."""
        self._backend.scroll(scroll_amount)


user = KeyboardMouseDriver()


def press(sequence: str, pause: float = 0.3) -> None:
    """Press keys described by a comma-separated sequence like ``up*2, down*3``."""
    logger.debug("input press sequence=%s", sequence)
    steps = [step.strip() for step in sequence.split(",")]

    for step in steps:
        if not step:
            continue

        key, separator, count_text = step.partition("*")
        key = key.strip()
        if not key:
            continue

        count = 1
        if separator:
            count_text = count_text.strip()
            if not count_text:
                logger.warning(
                    "Skipping press step with missing repeat count: %r", step
                )
                continue
            try:
                count = int(count_text)
            except ValueError:
                logger.warning(
                    "Skipping press step with invalid repeat count: %r", step
                )
                continue
            if count < 1:
                logger.warning(
                    "Skipping press step with non-positive repeat count: %r", step
                )
                continue

        for press_index in range(count):
            user.press(key)
            if press_index + 1 < count:
                time.sleep(pause)


def press_n_times(key: str, n: int, pause: float = 0.5) -> None:
    """Press the same key multiple times."""
    logger.debug("input press_n_times key=%s n=%s", key, n)
    for _ in range(n):
        user.press(key)
        time.sleep(pause)


def mouse_scroll_n_times(n: int, scroll_amount: int, pause: float) -> None:
    """Scroll the mouse wheel multiple times."""
    logger.debug("input mouse_scroll_n_times n=%s scroll_amount=%s", n, scroll_amount)
    for _ in range(n):
        user.scroll(scroll_amount)
        time.sleep(pause)


def mangohud_log_toggle() -> None:
    """Toggle MangoHud logging with Left Shift + F2 via ydotool."""
    logger.debug("input mangohud_log_toggle")
    time.sleep(1)
    user.key_down("leftshift")
    time.sleep(0.3)
    user.key_down("f2")
    time.sleep(0.3)
    user.key_up("f2")
    time.sleep(0.3)
    user.key_up("leftshift")
    time.sleep(1)
