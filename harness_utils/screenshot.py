"""Screenshot capture helpers."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
import mss
import numpy as np

from harness_utils.platform import is_linux


def _linux_screenshot_error(exc: Exception) -> RuntimeError:
    return RuntimeError(
        "Failed to capture screenshot on Linux. On Wayland/wlroots, install `grim`; "
        "on X11, verify DISPLAY is available and readable."
    )


def _grim_path() -> str | None:
    if is_linux() and os.getenv("WAYLAND_DISPLAY"):
        return shutil.which("grim")
    return None


def _run_grim(output_path: Path) -> None:
    grim = _grim_path()
    if grim is None:
        raise RuntimeError("grim is unavailable")

    result = subprocess.run(
        [grim, str(output_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        msg = f"Failed to capture screenshot with grim on Wayland: {stderr}"
        raise RuntimeError(msg)


def _take_mss_file(output_path: Path) -> None:
    try:
        with mss.mss() as sct:
            sct.shot(output=str(output_path))
    except Exception as exc:
        if is_linux():
            raise _linux_screenshot_error(exc) from exc
        raise


def take_screenshot_file(output_path: str | os.PathLike) -> None:
    """Capture a screenshot to a file."""
    path = Path(output_path)
    if _grim_path() is not None:
        _run_grim(path)
        return
    _take_mss_file(path)


def _capture_mss_grayscale() -> np.ndarray:
    try:
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor_1))
            return cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    except Exception as exc:
        if is_linux():
            raise _linux_screenshot_error(exc) from exc
        raise


def capture_screenshot_grayscale() -> np.ndarray:
    """Capture a screenshot as a grayscale array."""
    if _grim_path() is None:
        return _capture_mss_grayscale()

    with tempfile.TemporaryDirectory() as tmp:
        screenshot_path = Path(tmp) / "screenshot.png"
        _run_grim(screenshot_path)
        screenshot = cv2.imread(str(screenshot_path), cv2.IMREAD_GRAYSCALE)
        if screenshot is None:
            raise RuntimeError(f"Failed to read grim screenshot: {screenshot_path}")
        return screenshot
