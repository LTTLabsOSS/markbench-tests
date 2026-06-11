"""Platform input adapter."""

import logging
import math
import shutil
import subprocess
import time

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

WINDOWS_WHEEL_DELTA = 120

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


class _WindowsInputBackend:
    def __init__(self, controller: "InputController") -> None:
        import pydirectinput

        pydirectinput.FAILSAFE = controller.FAILSAFE
        self._pydirectinput = pydirectinput

    def press(self, key: str) -> None:
        self._pydirectinput.press(key)

    def keyDown(self, key: str) -> None:
        self._pydirectinput.keyDown(key)

    def keyUp(self, key: str) -> None:
        self._pydirectinput.keyUp(key)

    def hotkey(self, *keys: str) -> None:
        self._pydirectinput.hotkey(*keys)

    def click(self, x: int | None = None, y: int | None = None) -> None:
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
        logger.debug("ydotool args=%s", args)
        try:
            subprocess.run(
                [self._ydotool, *args],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            logger.debug(
                "ydotool failed args=%s stdout=%s stderr=%s",
                args,
                exc.stdout,
                exc.stderr,
                exc_info=True,
            )
            raise

    def press(self, key: str) -> None:
        self.keyDown(key)
        self.keyUp(key)

    def keyDown(self, key: str) -> None:
        self._run("key", f"{self._keycode(key)}:1")

    def keyUp(self, key: str) -> None:
        self._run("key", f"{self._keycode(key)}:0")

    def hotkey(self, *keys: str) -> None:
        for key in keys:
            self.keyDown(key)
        for key in reversed(keys):
            self.keyUp(key)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None and y is not None:
            self._run("mousemove", "--absolute", "0", "0")
            self._run("mousemove", str(x), str(y))
        self._run("click", "0xC0")

    def scroll(self, scroll_amount: int) -> None:
        """Scroll using existing Windows-style wheel delta units."""
        wheel_ticks = _windows_delta_to_wheel_ticks(scroll_amount)
        if wheel_ticks == 0:
            return
        self._run("mousemove", "--wheel", "-x", "0", "-y", str(wheel_ticks))


class InputController:
    """Keyboard and mouse input controller with Windows and Linux backends."""

    FAILSAFE: bool

    def __init__(self) -> None:
        self.FAILSAFE = True
        self._backend = self._create_backend()
        logger.debug("Initialized InputController FAILSAFE=%s", self.FAILSAFE)

    def _create_backend(self):
        if is_windows():
            return _WindowsInputBackend(self)
        if is_linux():
            return _YdotoolInputBackend()
        raise RuntimeError("Input is only supported on Windows and Linux")

    def press(self, key: str) -> None:
        """Press and release a key."""
        logger.debug("input press key=%s", key)
        self._backend.press(key)

    def keyDown(self, key: str) -> None:
        """Press and hold a key."""
        logger.debug("input keyDown key=%s", key)
        self._backend.keyDown(key)

    def keyUp(self, key: str) -> None:
        """Release a key."""
        logger.debug("input keyUp key=%s", key)
        self._backend.keyUp(key)

    def hotkey(self, *keys: str) -> None:
        """Press a key chord."""
        logger.debug("input hotkey keys=%s", keys)
        self._backend.hotkey(*keys)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Click the primary mouse button."""
        logger.debug("input click x=%s y=%s", x, y)
        self._backend.click(x=x, y=y)

    def scroll(self, scroll_amount: int) -> None:
        """Scroll the mouse wheel."""
        logger.debug("input scroll scroll_amount=%s", scroll_amount)
        self._backend.scroll(scroll_amount)


user = InputController()


def press_n_times(key: str, n: int, pause: float = 0.5) -> None:
    """Press the same key multiple times."""
    for _ in range(n):
        user.press(key)
        time.sleep(pause)


def mouse_scroll_n_times(n: int, scroll_amount: int, pause: float) -> None:
    """Scroll the mouse wheel multiple times."""
    for _ in range(n):
        user.scroll(scroll_amount)
        time.sleep(pause)


def mangohud_log_toggle() -> None:
    """Toggle MangoHud logging with Left Shift + F2 via ydotool."""
    time.sleep(1)
    user.keyDown("leftshift")
    time.sleep(0.3)
    user.keyDown("f2")
    time.sleep(0.3)
    user.keyUp("f2")
    time.sleep(0.3)
    user.keyUp("leftshift")
    time.sleep(1)
