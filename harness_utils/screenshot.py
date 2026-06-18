"""Screenshot capture helpers."""

import io
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import cv2
import mss
import numpy as np

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)


def _run_spectacle(output_path: Path) -> None:
    logger.debug("KDE Spectacle screenshot output=%s", output_path)
    subprocess.run(
        [
            "spectacle",
            "--fullscreen",
            "--background",
            "--nonotify",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _run_spectacle_png_bytes() -> bytes:
    logger.debug("KDE Spectacle screenshot to PNG bytes")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        output_path = Path(temp_file.name)
    output_path.unlink(missing_ok=True)

    try:
        _run_spectacle(output_path)
        image_bytes = output_path.read_bytes()
    finally:
        output_path.unlink(missing_ok=True)

    if not image_bytes:
        raise RuntimeError("Spectacle produced an empty screenshot")
    return image_bytes


def _decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Failed to decode Linux screenshot")
    return image


def _capture_dxcam_array() -> np.ndarray | None:
    logger.debug("Windows screenshot with dxcam")
    import dxcam

    camera = dxcam.create(output_idx=0, output_color="BGR")
    screenshot = camera.grab()
    if screenshot is None:
        return None
    return np.array(screenshot)


def _take_dxcam_file(output_path: Path) -> None:
    logger.debug("Windows screenshot with dxcam output=%s", output_path)
    screenshot = _capture_dxcam_array()
    if screenshot is None:
        raise RuntimeError("Failed to capture screenshot with dxcam")
    if not cv2.imwrite(str(output_path), screenshot):
        raise RuntimeError(f"Failed to write screenshot file: {output_path}")


def _capture_mss_array() -> np.ndarray:
    logger.debug("Screenshot with mss")
    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))


def _take_mss_file(output_path: Path) -> None:
    logger.debug("Screenshot with mss output=%s", output_path)
    with mss.mss() as sct:
        sct.shot(output=str(output_path))


def take_screenshot_file(output_path: str | os.PathLike) -> None:
    """Capture a screenshot to a file."""
    path = Path(output_path)
    logger.debug("Capturing screenshot file output=%s", path)
    if is_windows():
        _take_mss_file(path)
        return
    if is_linux():
        _run_spectacle(path)
        return
    raise RuntimeError("Screenshot capture is only supported on Windows and Linux")


def capture_screenshot_array(vulkan: bool = False) -> np.ndarray | None:
    """Capture a screenshot as an array."""
    if is_windows():
        if vulkan:
            return _capture_dxcam_array()
        return _capture_mss_array()
    if is_linux():
        return _decode_image_bytes(_run_spectacle_png_bytes())
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
        return io.BytesIO(_run_spectacle_png_bytes())

    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".png", screenshot)
    return io.BytesIO(encoded_image)
