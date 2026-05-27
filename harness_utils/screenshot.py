"""Screenshot capture helpers."""

import io
import logging
import os
import shutil
import subprocess
from pathlib import Path

import cv2
import dxcam
import mss
import numpy as np

from harness_utils.platform import is_linux

logger = logging.getLogger(__name__)


def _linux_screenshot_error(exc: Exception) -> RuntimeError:
    logger.warning("Linux screenshot capture failed: %s", exc)
    return RuntimeError(
        "Failed to capture screenshot on Linux. On Wayland/wlroots, install `grim`; "
        "on X11, verify DISPLAY is available and readable."
    )


def _grim_path() -> str | None:
    logger.debug(
        "Checking grim backend WAYLAND_DISPLAY=%s", os.getenv("WAYLAND_DISPLAY")
    )
    if is_linux() and os.getenv("WAYLAND_DISPLAY"):
        grim = shutil.which("grim")
        logger.debug("Resolved grim path=%s", grim)
        return grim
    return None


def _run_grim(output_path: Path) -> None:
    logger.info("Attempting Wayland screenshot with grim output=%s", output_path)
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
    logger.info("Captured Wayland screenshot with grim output=%s", output_path)


def _take_mss_file(output_path: Path) -> None:
    logger.info("Attempting screenshot with mss output=%s", output_path)
    try:
        with mss.mss() as sct:
            sct.shot(output=str(output_path))
    except Exception as exc:
        if is_linux():
            raise _linux_screenshot_error(exc) from exc
        raise
    logger.info("Captured screenshot with mss output=%s", output_path)


def take_screenshot_file(output_path: str | os.PathLike) -> None:
    """Capture a screenshot to a file."""
    path = Path(output_path)
    logger.info("Capturing screenshot file output=%s", path)
    if _grim_path() is not None:
        _run_grim(path)
        return
    _take_mss_file(path)


def capture_screenshot_array(vulkan: bool = False) -> np.ndarray | None:
    """Capture a screenshot as an array."""
    if vulkan:
        camera = dxcam.create(output_idx=0, output_color="BGR")
        screenshot = camera.grab()
        if screenshot is None:
            return None
        return np.array(screenshot)

    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))


def capture_screenshot_jpg_bytes(vulkan: bool = False) -> io.BytesIO | None:
    """Capture a screenshot and encode it as JPG bytes."""
    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".jpg", screenshot)
    return io.BytesIO(encoded_image)


def capture_screenshot_png_bytes(vulkan: bool = False) -> io.BytesIO | None:
    """Capture a screenshot and encode it as PNG bytes."""
    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".png", screenshot)
    return io.BytesIO(encoded_image)
