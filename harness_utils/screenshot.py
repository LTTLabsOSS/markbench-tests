"""Screenshot capture helpers."""

import io
import logging
import os
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)


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


def _run_grim_stdout() -> bytes:
    logger.info("Attempting Wayland screenshot with grim stdout")
    grim = _grim_path()
    if grim is None:
        raise RuntimeError("grim is unavailable")

    result = subprocess.run(
        [grim, "-"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        stderr = result.stderr.decode(errors="replace").strip()
        msg = f"Failed to capture screenshot with grim on Wayland: {stderr}"
        raise RuntimeError(msg)
    logger.info("Captured Wayland screenshot with grim stdout")
    return result.stdout


def _decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Failed to decode Wayland screenshot captured with grim")
    return image


def _capture_dxcam_array() -> np.ndarray | None:
    logger.info("Attempting Windows screenshot with dxcam")
    import dxcam

    camera = dxcam.create(output_idx=0, output_color="BGR")
    screenshot = camera.grab()
    if screenshot is None:
        return None
    logger.info("Captured Windows screenshot with dxcam")
    return np.array(screenshot)


def _take_dxcam_file(output_path: Path) -> None:
    logger.info("Attempting Windows screenshot with dxcam output=%s", output_path)
    screenshot = _capture_dxcam_array()
    if screenshot is None:
        raise RuntimeError("Failed to capture screenshot with dxcam")
    if not cv2.imwrite(str(output_path), screenshot):
        raise RuntimeError(f"Failed to write screenshot file: {output_path}")
    logger.info("Captured Windows screenshot with dxcam output=%s", output_path)


def take_screenshot_file(output_path: str | os.PathLike) -> None:
    """Capture a screenshot to a file."""
    path = Path(output_path)
    logger.info("Capturing screenshot file output=%s", path)
    if is_windows():
        _take_dxcam_file(path)
        return
    if is_linux():
        _run_grim(path)
        return
    raise RuntimeError("Screenshot capture is only supported on Windows and Linux")


def capture_screenshot_array(vulkan: bool = False) -> np.ndarray | None:
    """Capture a screenshot as an array."""
    if is_windows():
        return _capture_dxcam_array()
    if is_linux():
        return _decode_image_bytes(_run_grim_stdout())
    raise RuntimeError("Screenshot capture is only supported on Windows and Linux")


def capture_screenshot_jpg_bytes(vulkan: bool = False) -> io.BytesIO | None:
    """Capture a screenshot and encode it as JPG bytes."""
    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".jpg", screenshot)
    return io.BytesIO(encoded_image)


def capture_screenshot_png_bytes(vulkan: bool = False) -> io.BytesIO | None:
    """Capture a screenshot and encode it as PNG bytes."""
    if is_linux():
        return io.BytesIO(_run_grim_stdout())

    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".png", screenshot)
    return io.BytesIO(encoded_image)
