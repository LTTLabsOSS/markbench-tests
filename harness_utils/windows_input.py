"""Windows input using scan-code SendInput and PyAutoGUI-style mouse calls.

- Text: US-keyboard ASCII, Caps Lock off, no held modifiers.
- Mouse: SetCursorPos for movement; mouse_event for buttons and wheel.
- DPI: requests system awareness; preserves any preconfigured process mode.
- Thanks to PyAutoGUI for mouse-behavior references.
"""

from __future__ import annotations

import ctypes
import math
import os
import time
from collections.abc import Callable, Sequence
from typing import Any, Protocol, cast

WORD = ctypes.c_uint16
DWORD = ctypes.c_uint32
LONG = ctypes.c_int32
UINT = ctypes.c_uint32
ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32

DPI_AWARENESS_CONTEXT_SYSTEM_AWARE = -2
ERROR_ACCESS_DENIED = 5


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", WORD),
        ("wScan", WORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


# Required for the native INPUT union size, even when sending only keyboard input.
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class _INPUTUNION(ctypes.Union):
    _fields_ = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT))


class INPUT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = (("type", DWORD), ("value", _INPUTUNION))


INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_WHEEL = 0x0800

# PC set-1 scan codes; E0 is represented by flags, never packed into wScan.
_NAMED_SCANS = {
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0A,
    "0": 0x0B,
    "-": 0x0C,
    "=": 0x0D,
    "[": 0x1A,
    "]": 0x1B,
    ";": 0x27,
    "'": 0x28,
    "`": 0x29,
    "\\": 0x2B,
    ",": 0x33,
    ".": 0x34,
    "/": 0x35,
    "a": 0x1E,
    "b": 0x30,
    "c": 0x2E,
    "d": 0x20,
    "e": 0x12,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "i": 0x17,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    "m": 0x32,
    "n": 0x31,
    "o": 0x18,
    "p": 0x19,
    "q": 0x10,
    "r": 0x13,
    "s": 0x1F,
    "t": 0x14,
    "u": 0x16,
    "v": 0x2F,
    "w": 0x11,
    "x": 0x2D,
    "y": 0x15,
    "z": 0x2C,
    "escape": 0x01,
    "backspace": 0x0E,
    "tab": 0x0F,
    "enter": 0x1C,
    "space": 0x39,
    "shiftleft": 0x2A,
    "ctrlleft": 0x1D,
    "altleft": 0x38,
    "winleft": 0x5B,
    "f1": 0x3B,
    "f2": 0x3C,
    "f3": 0x3D,
    "f4": 0x3E,
    "f5": 0x3F,
    "f6": 0x40,
    "f7": 0x41,
    "f8": 0x42,
    "f9": 0x43,
    "f10": 0x44,
    "f11": 0x57,
    "f12": 0x58,
    "home": 0x47,
    "up": 0x48,
    "pageup": 0x49,
    "left": 0x4B,
    "right": 0x4D,
    "end": 0x4F,
    "down": 0x50,
    "pagedown": 0x51,
    "insert": 0x52,
    "delete": 0x53,
}

_EXTENDED_KEYS = frozenset(
    (
        "up",
        "down",
        "left",
        "right",
        "home",
        "end",
        "pageup",
        "pagedown",
        "insert",
        "delete",
        "winleft",
    )
)
_KEY_ALIASES = {
    "esc": "escape",
    "return": "enter",
    "\n": "enter",
    "\r": "enter",
    "\t": "tab",
    " ": "space",
    "shift": "shiftleft",
    "ctrl": "ctrlleft",
    "alt": "altleft",
    "win": "winleft",
}

# Shifted US glyph -> unshifted physical key, including every uppercase letter.
_SHIFTED_TEXT_KEYS = {
    **{character.upper(): character for character in "abcdefghijklmnopqrstuvwxyz"},
    "!": "1",
    "@": "2",
    "#": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    ")": "0",
    "_": "-",
    "+": "=",
    "{": "[",
    "}": "]",
    ":": ";",
    '"': "'",
    "~": "`",
    "|": "\\",
    "<": ",",
    ">": ".",
    "?": "/",
}
_TEXT_SCANS = {
    character: scan for character, scan in _NAMED_SCANS.items() if len(character) == 1
}
_TEXT_SCANS.update(
    {
        " ": _NAMED_SCANS["space"],
        "\n": _NAMED_SCANS["enter"],
        "\r": _NAMED_SCANS["enter"],
        "\t": _NAMED_SCANS["tab"],
    }
)
_TEXT_SCANS.update(
    {character: _NAMED_SCANS[key] for character, key in _SHIFTED_TEXT_KEYS.items()}
)

SUPPORTED_NAMED_KEYS = frozenset(_NAMED_SCANS) | frozenset(_KEY_ALIASES)
SUPPORTED_TEXT_CHARACTERS = frozenset(_TEXT_SCANS)


class InputTransport(Protocol):
    def send_input(self, packets: Sequence[INPUT], cb_size: int) -> int: ...

    def get_last_error(self) -> int: ...

    def set_cursor_pos(self, x: int, y: int) -> None: ...

    def mouse_event(self, flags: int, data: int = 0) -> None: ...


def _keyboard_input(scan: int, flags: int = 0) -> INPUT:
    packet = INPUT()
    packet.type = INPUT_KEYBOARD
    packet.ki = KEYBDINPUT(0, scan, KEYEVENTF_SCANCODE | flags, 0, 0)
    return packet


class User32Transport:
    """Thin, lazy native binding for the Windows input backend."""

    def __init__(self) -> None:
        self._user32: Any = None
        if os.name != "nt":
            raise OSError("User32 input is only available on Windows")

        self._user32 = cast(Any, ctypes).WinDLL("user32", use_last_error=True)
        send_input = self._user32.SendInput
        send_input.argtypes = (UINT, ctypes.POINTER(INPUT), ctypes.c_int)
        send_input.restype = UINT
        set_cursor_pos = self._user32.SetCursorPos
        set_cursor_pos.argtypes = (ctypes.c_int, ctypes.c_int)
        set_cursor_pos.restype = ctypes.c_int
        mouse_event = self._user32.mouse_event
        mouse_event.argtypes = (DWORD, DWORD, DWORD, DWORD, ULONG_PTR)
        mouse_event.restype = None
        set_process_dpi_aware = self._user32.SetProcessDpiAwarenessContext
        set_process_dpi_aware.argtypes = (ctypes.c_void_p,)
        set_process_dpi_aware.restype = ctypes.c_int
        cast(Any, ctypes).set_last_error(0)
        if not set_process_dpi_aware(DPI_AWARENESS_CONTEXT_SYSTEM_AWARE):
            error = self.get_last_error()
            # Preserve DPI mode already set by a manifest or an earlier library.
            if error != ERROR_ACCESS_DENIED:
                raise OSError(error, "SetProcessDpiAwarenessContext failed")

    def send_input(self, packets: Sequence[INPUT], cb_size: int) -> int:
        array = (INPUT * len(packets))(*packets)
        cast(Any, ctypes).set_last_error(0)
        return int(self._user32.SendInput(len(packets), array, cb_size))

    def get_last_error(self) -> int:
        return int(cast(Any, ctypes).get_last_error())

    def set_cursor_pos(self, x: int, y: int) -> None:
        if not self._user32.SetCursorPos(x, y):
            raise OSError(self.get_last_error(), "SetCursorPos failed")

    def mouse_event(self, flags: int, data: int = 0) -> None:
        self._user32.mouse_event(flags, 0, 0, data, 0)


class WindowsInput:
    """The narrow keyboard and mouse surface required by the game harness."""

    def __init__(
        self,
        transport: InputTransport | None = None,
        *,
        delay: float = 0.1,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not math.isfinite(delay) or delay < 0:
            raise ValueError("delay must be finite and non-negative")
        self._transport = User32Transport() if transport is None else transport
        self.delay = delay
        self._sleep = sleeper

    def _send(self, packets: Sequence[INPUT]) -> None:
        requested = len(packets)
        inserted = self._transport.send_input(packets, ctypes.sizeof(INPUT))
        if inserted != requested:
            error = self._transport.get_last_error()
            raise OSError(
                error,
                f"SendInput inserted {inserted} of {requested} requested events",
            )

    def _cleanup(self, packets: Sequence[INPUT]) -> None:
        try:
            self._send(packets)
        except OSError:
            pass

    @staticmethod
    def _normalize_key(key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        normalized = key.lower()
        normalized = _KEY_ALIASES.get(normalized, normalized)
        if normalized not in _NAMED_SCANS:
            raise ValueError(f"Unsupported key: {key!r}")
        return normalized

    @staticmethod
    def _key_down_packets(key: str) -> list[INPUT]:
        flags = KEYEVENTF_EXTENDEDKEY if key in _EXTENDED_KEYS else 0
        return [_keyboard_input(_NAMED_SCANS[key], flags)]

    @staticmethod
    def _key_up_packets(key: str) -> list[INPUT]:
        flags = KEYEVENTF_KEYUP
        if key in _EXTENDED_KEYS:
            flags |= KEYEVENTF_EXTENDEDKEY
        return [_keyboard_input(_NAMED_SCANS[key], flags)]

    def key_down(self, key: str) -> None:
        normalized = self._normalize_key(key)
        cleanup = self._key_up_packets(normalized)
        try:
            self._send(self._key_down_packets(normalized))
        except OSError:
            self._cleanup(cleanup)
            raise
        self._sleep(self.delay)

    def key_up(self, key: str) -> None:
        normalized = self._normalize_key(key)
        packets = self._key_up_packets(normalized)
        try:
            self._send(packets)
        except OSError:
            self._cleanup(packets)
            raise
        self._sleep(self.delay)

    def press(self, key: str) -> None:
        normalized = self._normalize_key(key)
        up_packets = self._key_up_packets(normalized)
        packets = self._key_down_packets(normalized)
        try:
            self._send(packets)
            self._sleep(self.delay)
            self._send(up_packets)
        except BaseException as error:
            try:
                self._cleanup(up_packets)
            except BaseException:
                raise error from None
            raise
        self._sleep(self.delay)  # key-up pause
        self._sleep(self.delay)  # outer press pause

    def write(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        unsupported = sorted(set(text) - SUPPORTED_TEXT_CHARACTERS)
        if unsupported:
            raise ValueError(f"Unsupported text characters: {unsupported!r}")

        for character in text:
            scan = _TEXT_SCANS[character]
            if character in _SHIFTED_TEXT_KEYS:
                release_packets = [
                    _keyboard_input(scan, KEYEVENTF_KEYUP),
                    _keyboard_input(_NAMED_SCANS["shiftleft"], KEYEVENTF_KEYUP),
                ]
                packets = [
                    _keyboard_input(_NAMED_SCANS["shiftleft"]),
                    _keyboard_input(scan),
                ]
            else:
                release_packets = [_keyboard_input(scan, KEYEVENTF_KEYUP)]
                packets = [_keyboard_input(scan)]
            try:
                self._send(packets)
                self._sleep(self.delay)
                self._send(release_packets)
            except BaseException as error:
                try:
                    self._cleanup(release_packets)
                except BaseException:
                    raise error from None
                raise
            self._sleep(self.delay)  # key-up pause
        self._sleep(self.delay)  # outer write pause, including empty text

    def move_mouse(self, x: int, y: int) -> None:
        self._transport.set_cursor_pos(x, y)
        self._sleep(self.delay)

    def mouse_down(self) -> None:
        self._transport.mouse_event(MOUSEEVENTF_LEFTDOWN)
        self._sleep(self.delay)

    def mouse_up(self) -> None:
        self._transport.mouse_event(MOUSEEVENTF_LEFTUP)
        self._sleep(self.delay)

    def click(self, hold: float = 0.0) -> None:
        if not math.isfinite(hold) or hold < 0:
            raise ValueError("hold must be finite and non-negative")
        self._transport.mouse_event(MOUSEEVENTF_LEFTDOWN)
        try:
            self._sleep(hold)
        finally:
            self._transport.mouse_event(MOUSEEVENTF_LEFTUP)
        self._sleep(self.delay)

    def scroll(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("wheel amount must be an integer")
        if not -(1 << 31) <= amount < (1 << 31):
            raise ValueError("wheel amount must fit in a signed 32-bit integer")
        self._transport.mouse_event(MOUSEEVENTF_WHEEL, ctypes.c_uint32(amount).value)
        self._sleep(self.delay)
