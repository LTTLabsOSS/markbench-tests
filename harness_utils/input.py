"""Platform input adapter."""

import logging
import shutil
import subprocess

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)


_YTODOOL_KEYS = {
    "left": 105,
    "right": 106,
    "up": 103,
    "down": 108,
    "enter": 28,
    "b": 48,
    "3": 4,
}


class InputController:
    """Keyboard and mouse input controller with Windows and Linux backends."""

    FAILSAFE: bool

    def __init__(self) -> None:
        self.FAILSAFE = True
        logger.debug("Initialized InputController FAILSAFE=%s", self.FAILSAFE)

    def _windows_backend(self):
        logger.debug("Resolving Windows pydirectinput backend")
        if not is_windows():
            raise RuntimeError("pydirectinput input backend requires Windows")
        import pydirectinput

        pydirectinput.FAILSAFE = self.FAILSAFE
        logger.debug("Resolved pydirectinput backend FAILSAFE=%s", self.FAILSAFE)
        return pydirectinput

    def _ydotool_path(self) -> str:
        logger.debug("Resolving ydotool executable")
        if not is_linux():
            raise RuntimeError("ydotool input backend requires Linux")
        ydotool = shutil.which("ydotool")
        if ydotool is None:
            raise RuntimeError("Linux input requires `ydotool` on PATH")
        logger.debug("Resolved ydotool executable: %s", ydotool)
        return ydotool

    def _ydotool_keycode(self, key: str) -> int:
        normalized_key = key.lower()
        try:
            keycode = _YTODOOL_KEYS[normalized_key]
            logger.debug("Mapped ydotool key key=%s keycode=%s", key, keycode)
            return keycode
        except KeyError as exc:
            supported = ", ".join(sorted(_YTODOOL_KEYS))
            raise RuntimeError(f"Unsupported ydotool key `{key}`; supported: {supported}") from exc

    def _run_ydotool(self, *args: str) -> None:
        command = [self._ydotool_path(), *args]
        logger.info("Running ydotool command: %s", " ".join(command))
        subprocess.run(command, check=True)

    def press(self, key: str) -> None:
        """Press and release a key."""
        logger.info("Attempting input press key=%s", key)
        if is_windows():
            self._windows_backend().press(key)
            return
        if is_linux():
            self.keyDown(key)
            self.keyUp(key)
            return
        raise RuntimeError("Input press is only supported on Windows and Linux")

    def keyDown(self, key: str) -> None:
        """Press and hold a key."""
        logger.info("Attempting input keyDown key=%s", key)
        if is_windows():
            self._windows_backend().keyDown(key)
            return
        if is_linux():
            keycode = self._ydotool_keycode(key)
            self._run_ydotool("key", f"{keycode}:1")
            return
        raise RuntimeError("Input keyDown is only supported on Windows and Linux")

    def keyUp(self, key: str) -> None:
        """Release a key."""
        logger.info("Attempting input keyUp key=%s", key)
        if is_windows():
            self._windows_backend().keyUp(key)
            return
        if is_linux():
            keycode = self._ydotool_keycode(key)
            self._run_ydotool("key", f"{keycode}:0")
            return
        raise RuntimeError("Input keyUp is only supported on Windows and Linux")

    def hotkey(self, *keys: str) -> None:
        """Press a key chord."""
        logger.info("Attempting input hotkey keys=%s", keys)
        if is_windows():
            self._windows_backend().hotkey(*keys)
            return
        if is_linux():
            for key in keys:
                self.keyDown(key)
            for key in reversed(keys):
                self.keyUp(key)
            return
        raise RuntimeError("Input hotkey is only supported on Windows and Linux")

    def click(self, x: int | None = None, y: int | None = None) -> None:
        """Click the primary mouse button."""
        logger.info("Attempting input click x=%s y=%s", x, y)
        if is_windows():
            self._windows_backend().click(x=x, y=y)
            return
        if is_linux():
            if x is not None and y is not None:
                self._run_ydotool("mousemove", "--absolute", str(x), str(y))
            self._run_ydotool("click", "0xC0")
            return
        raise RuntimeError("Input click is only supported on Windows and Linux")


user = InputController()
