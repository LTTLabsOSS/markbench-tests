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
    # Letters
    "a": 30,
    "b": 48,
    "c": 46,
    "d": 32,
    "e": 18,
    "f": 33,
    "q": 16,
    "r": 19,
    "s": 31,
    "w": 17,
    "x": 45,
    "z": 44,
    # Numbers
    "1": 2,
    "3": 4,
    # Modifiers
    "altleft": 56,
    "leftshift": 42,
    # Direction and navigation
    "down": 108,
    "left": 105,
    "pagedown": 109,
    "right": 106,
    "up": 103,
    # Control keys
    "backspace": 14,
    "enter": 28,
    "escape": 1,
    "space": 57,
    "tab": 15,
    # Function keys
    "f1": 59,
    "f2": 60,
    "f3": 61,
    "f5": 63,
    # Symbols
    "`": 41,
    "\\": 43,
    "[": 26,
    "]": 27,
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
        vars(self._pydirectinput)["FAILSAFE"] = controller.FAILSAFE

    def press(self, key: str) -> None:
        self._pydirectinput.press(key)

    def write(self, text: str) -> None:
        self._pydirectinput.write(text)

    def key_down(self, key: str) -> None:
        self._pydirectinput.keyDown(key)

    def key_up(self, key: str) -> None:
        self._pydirectinput.keyUp(key)

    def hotkey(self, *keys: str) -> None:
        self._pydirectinput.hotkey(*keys)

    def move_mouse(self, x: int, y: int) -> None:
        self._pydirectinput.moveTo(x=x, y=y)

    def click(self, hold: float = 0.0) -> None:
        self._pydirectinput.mouseDown()
        time.sleep(hold)
        self._pydirectinput.mouseUp()

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

    def write(self, text: str) -> None:
        self._run("type", text)

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

    def click(self, hold: float = 0.0) -> None:
        self._run("click", "0x40")
        time.sleep(hold)
        self._run("click", "0x80")

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

    def write(self, text: str) -> None:
        """Type text."""
        self._backend.write(text)

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

    def click(
        self,
        x: int | None = None,
        y: int | None = None,
        hold: float = 0.0,
        pre_click_delay: float = 0.2,
    ) -> None:
        """Optionally move the pointer, wait, and click the primary mouse button."""
        if x is not None and y is not None:
            self.move_mouse(x, y)
        time.sleep(pre_click_delay)
        self._backend.click(hold)

    def scroll(self, scroll_amount: int) -> None:
        """Scroll the mouse wheel."""
        self._backend.scroll(scroll_amount)


user = KeyboardMouseDriver()


def move_mouse(x: int, y: int) -> None:
    """Move the mouse pointer without clicking."""
    user.move_mouse(x, y)


def write(text: str) -> None:
    """Type text."""
    user.write(text)


def click(
    x: int | None = None,
    y: int | None = None,
    hold: float = 0.0,
    pre_click_delay: float = 0.2,
) -> None:
    """Optionally move the pointer, then wait before and after clicking."""
    user.click(x, y, hold, pre_click_delay)
    time.sleep(pre_click_delay)


def hold(key: str, duration: float) -> None:
    """Hold one key for the requested duration."""
    user.key_down(key)
    time.sleep(duration)
    user.key_up(key)


def press(sequence: str, pause: float = 0.5) -> None:
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

        for _ in range(count):
            user.press(key)
            time.sleep(pause)


def scroll(scroll_amount: int, count: int = 1, pause: float = 0.5) -> None:
    """Scroll the mouse wheel one or more times."""
    logger.debug("input scroll scroll_amount=%s count=%s", scroll_amount, count)
    for _ in range(count):
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
