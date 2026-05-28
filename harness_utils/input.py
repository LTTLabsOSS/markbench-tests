"""Platform input adapter."""

import logging
import subprocess
from pathlib import Path
from time import sleep

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)

DEFAULT_YDOTOOL_SOCKET = Path("/tmp/.ydotool_socket")
YDOTOOLD_STARTUP_WAIT_SECONDS = 1


_PYDOTOOL_KEYS = {
    "left": "KEY_LEFT",
    "right": "KEY_RIGHT",
    "up": "KEY_UP",
    "down": "KEY_DOWN",
    "enter": "KEY_ENTER",
    "b": "KEY_B",
    "3": "KEY_3",
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


class _PydotoolInputBackend:
    def __init__(self) -> None:
        import pydotool

        if not DEFAULT_YDOTOOL_SOCKET.exists():
            subprocess.Popen(
                ["ydotoold", "--socket-path", str(DEFAULT_YDOTOOL_SOCKET)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(YDOTOOLD_STARTUP_WAIT_SECONDS * 10):
                if DEFAULT_YDOTOOL_SOCKET.exists():
                    break
                sleep(0.1)

        pydotool.init(str(DEFAULT_YDOTOOL_SOCKET))
        self._pydotool = pydotool

    def _keycode(self, key: str) -> int:
        normalized_key = key.lower()
        try:
            key_name = _PYDOTOOL_KEYS[normalized_key]
            return getattr(self._pydotool, key_name)
        except KeyError as exc:
            supported = ", ".join(sorted(_PYDOTOOL_KEYS))
            raise RuntimeError(
                f"Unsupported pydotool key `{key}`; supported: {supported}"
            ) from exc

    def press(self, key: str) -> None:
        self._pydotool.input_key(self._keycode(key))

    def keyDown(self, key: str) -> None:
        self._pydotool.key(self._keycode(key), True)

    def keyUp(self, key: str) -> None:
        self._pydotool.key(self._keycode(key), False)

    def hotkey(self, *keys: str) -> None:
        self._pydotool.key_combination([self._keycode(key) for key in keys])

    def click(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None and y is not None:
            self._pydotool.mouse_move((x, y), True)
        self._pydotool.left_click()


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
            return _PydotoolInputBackend()
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
