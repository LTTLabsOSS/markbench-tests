from pathlib import Path
from shutil import copy

import yaml

from harness_utils.screenshot import capture_screenshot_png_bytes


def copy_artifact(source: str | Path, directory: str | Path) -> None:
    """Copy a file into the artifact directory, preserving its basename."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    copy(source, directory)


def create_artifacts_manifest(directory: str | Path) -> None:
    directory = Path(directory)
    artifacts = []
    for path in directory.iterdir():
        if not path.is_file() or path.name == "artifacts.yaml":
            continue
        if path.suffix == ".png":
            artifact_type = "results_image" if "result" in path.name else "config_image"
        else:
            artifact_type = "config_text"
        artifacts.append({"filename": path.name, "type": artifact_type})
    (directory / "artifacts.yaml").write_text(
        yaml.safe_dump(artifacts, sort_keys=False)
    )


def capture_and_save_screenshot(path: str | Path, vulkan: bool = False) -> None:
    """Capture a PNG screenshot and write it to path."""
    image_bytes = capture_screenshot_png_bytes(vulkan=vulkan)
    if image_bytes is None:
        raise RuntimeError("Failed to capture screenshot")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(image_bytes.getbuffer())
