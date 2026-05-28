"""Platform input adapter."""

import logging
import shutil
import subprocess
from contextlib import suppress

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

YDOTOOL_KEY_HOLD_MS = 50

_YDOTOOL_KEYS = {
    "left": 105,
    "right": 106,
    "up": 103,
    "down": 108,
    "enter": 28,
    "b": 48,
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
        subprocess.run([self._ydotool, *args], check=True)

    def press(self, key: str) -> None:
        keycode = self._keycode(key)
        try:
            self._run(
                "key",
                "--key-delay",
                str(YDOTOOL_KEY_HOLD_MS),
                f"{keycode}:1",
                f"{keycode}:0",
            )
        except subprocess.CalledProcessError:
            with suppress(subprocess.CalledProcessError):
                self._run("key", f"{keycode}:0")
            raise

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
            self._run("mousemove", "--absolute", str(x), str(y))
        self._run("click", "0xC0")


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

    def keyDown(self, key: str) -> None:
        """Press and hold a key."""
        logger.info("Attempting input keyDown key=%s", key)
        self._backend.keyDown(key)

    def keyUp(self, key: str) -> None:
        """Release a key."""
        logger.info("Attempting input keyUp key=%s", key)
        self._backend.keyUp(key)

    def hotkey(self, *keys: str) -> None:
        """Press a key chord."""
        logger.info("Attempting input hotkey keys=%s", keys)
        self._backend.hotkey(*keys)

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Click the primary mouse button."""
        logger.info("Attempting input click x=%s y=%s", x, y)
        self._backend.click(x=x, y=y)


user = InputController()
