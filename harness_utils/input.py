"""Platform input adapter."""

import logging
import shutil
import subprocess
import time

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

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
        self._ydotool = shutil.which("ydotool")
        if self._ydotool is None:
            raise RuntimeError("Linux input requires `ydotool` on PATH")

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
        logger.info("Attempting ydotool command args=%s", args)
        try:
            subprocess.run([self._ydotool, *args], check=True)
        except subprocess.CalledProcessError:
            logger.exception("Failed ydotool command args=%s", args)
            raise
        logger.info("Completed ydotool command args=%s", args)

    def press(self, key: str) -> None:
        keycode = self._keycode(key)
        logger.info("Attempting ydotool press key=%s keycode=%s", key, keycode)
        self.keyDown(key)
        self.keyUp(key)
        logger.info("Completed ydotool press key=%s keycode=%s", key, keycode)

    def keyDown(self, key: str) -> None:
        keycode = self._keycode(key)
        logger.info("Attempting ydotool keyDown key=%s keycode=%s", key, keycode)
        self._run("key", f"{keycode}:1")
        logger.info("Completed ydotool keyDown key=%s keycode=%s", key, keycode)

    def keyUp(self, key: str) -> None:
        keycode = self._keycode(key)
        logger.info("Attempting ydotool keyUp key=%s keycode=%s", key, keycode)
        self._run("key", f"{keycode}:0")
        logger.info("Completed ydotool keyUp key=%s keycode=%s", key, keycode)

    def hotkey(self, *keys: str) -> None:
        for key in keys:
            self.keyDown(key)
        for key in reversed(keys):
            self.keyUp(key)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None and y is not None:
            self._run("mousemove", "--absolute", str(x), str(y))
        self._run("click", "0xC0")

    def scroll(self, scroll_amount: int) -> None:
        self._run("mousemove", "--wheel", "-x", "0", "-y", str(scroll_amount))


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
        logger.info("Attempting input press key=%s", key)
        self._backend.press(key)
        logger.info("Completed input press key=%s", key)

    def keyDown(self, key: str) -> None:
        """Press and hold a key."""
        logger.info("Attempting input keyDown key=%s", key)
        self._backend.keyDown(key)
        logger.info("Completed input keyDown key=%s", key)

    def keyUp(self, key: str) -> None:
        """Release a key."""
        logger.info("Attempting input keyUp key=%s", key)
        self._backend.keyUp(key)
        logger.info("Completed input keyUp key=%s", key)

    def hotkey(self, *keys: str) -> None:
        """Press a key chord."""
        logger.info("Attempting input hotkey keys=%s", keys)
        self._backend.hotkey(*keys)
        logger.info("Completed input hotkey keys=%s", keys)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Click the primary mouse button."""
        logger.info("Attempting input click x=%s y=%s", x, y)
        self._backend.click(x=x, y=y)

    def scroll(self, scroll_amount: int) -> None:
        """Scroll the mouse wheel."""
        logger.info("Attempting input scroll scroll_amount=%s", scroll_amount)
        self._backend.scroll(scroll_amount)
        logger.info("Completed input scroll scroll_amount=%s", scroll_amount)


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
