from pathlib import Path
from shutil import copy, rmtree

from harness_utils.screenshot import capture_screenshot_png_bytes


def reset_artifacts(directory: str | Path) -> None:
    """Replace the artifact directory with an empty directory."""
    directory = Path(directory)
    if directory.exists():
        rmtree(directory)
    directory.mkdir(parents=True)


def copy_artifact(source: str | Path, directory: str | Path) -> None:
    """Copy a file into the artifact directory, preserving its basename."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    copy(source, directory)


def capture_and_save_screenshot(path: str | Path, vulkan: bool = False) -> None:
    """Capture a PNG screenshot and write it to path."""
    image_bytes = capture_screenshot_png_bytes(vulkan=vulkan)
    if image_bytes is None:
        raise RuntimeError("Failed to capture screenshot")
    Path(path).write_bytes(image_bytes.getbuffer())
