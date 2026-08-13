"""Screenshot capture helpers."""

import io
import subprocess
import tempfile
from pathlib import Path

import cv2
import mss
import numpy as np

from harness_utils.platform import is_linux, is_windows


def _run_spectacle(output_path: Path):
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
    import dxcam

    camera = dxcam.create(output_idx=0, output_color="BGR")
    screenshot = camera.grab()
    if screenshot is None:
        return None
    camera.release()
    return np.array(screenshot)


def _take_dxcam_file(output_path: Path) -> None:
    screenshot = _capture_dxcam_array()
    if screenshot is None:
        raise RuntimeError("Failed to capture screenshot with dxcam")
    if not cv2.imwrite(str(output_path), screenshot):
        raise RuntimeError(f"Failed to write screenshot file: {output_path}")


def _capture_mss_array() -> np.ndarray:
    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))


def take_mss_file(output_path: Path) -> None:
    with mss.mss() as sct:
        sct.shot(output=str(output_path))


def capture_screenshot_file(output_path: Path):
    """Capture a screenshot to a file."""
    if is_windows():
        _take_dxcam_file(output_path)
    else:
        _run_spectacle(output_path)


def capture_screenshot_array(vulkan: bool = False) -> np.ndarray | None:
    """Capture a screenshot as an array."""
    if is_windows():
        if vulkan:
            return _capture_dxcam_array()
        return _capture_mss_array()
    if is_linux():
        return _decode_image_bytes(_run_spectacle_png_bytes())
    raise RuntimeError("Screenshot capture is only supported on Windows and Linux")


def _crop_screenshot(screenshot: np.ndarray, crop: str | None) -> np.ndarray:
    if crop is None:
        return screenshot

    height, width = screenshot.shape[:2]
    if crop == "top_left":
        return screenshot[0 : height // 2, 0 : width // 2]
    if crop == "top_right":
        return screenshot[0 : height // 2, width // 2 : width]
    raise ValueError(f"Unsupported screenshot crop: {crop}")


def capture_screenshot_jpg_bytes(
    vulkan: bool = False, crop: str | None = None
) -> io.BytesIO | None:
    """Capture a screenshot and encode it as JPG bytes."""
    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    screenshot = _crop_screenshot(screenshot, crop)
    _, encoded_image = cv2.imencode(".jpg", screenshot)
    return io.BytesIO(encoded_image)


def capture_screenshot_png_bytes(vulkan: bool = False):
    """Capture a screenshot and encode it as PNG bytes."""
    if is_linux():
        return io.BytesIO(_run_spectacle_png_bytes())

    screenshot = capture_screenshot_array(vulkan)
    if screenshot is None:
        return None

    _, encoded_image = cv2.imencode(".png", screenshot)
    return io.BytesIO(encoded_image)
