"""Utility functions for GravityMark test script"""
from argparse import ArgumentParser, Namespace
import re
from pathlib import Path

API_OPTIONS = [
    "vulkan",
    "opengl",
    # "opengles",
    "direct3d12",
    "direct3d11",
    # "metal"
]

CLI_OPTIONS = {
    # "-image": str(IMAGE_PATH),
    "-fullscreen": "1",
    "-fps": "1",
    "-info": "1",
    "-sensors": "1",
    "-benchmark": "1",
    "-close": "1",
    "-status": "1"
}

def friendly_test_param(api: str) -> str:
    """return a friendlier string given the API harness argument"""
    if api == "vulkan":
        return "Vulkan"
    if api == "opengl":
        return "OpenGL"
    if api == "direct3d12":
        return "DX12"
    if api == "direct3d11":
        return "DX11"
    return api

def get_args() -> Namespace:
    """Get command line arguments for test script"""
    parser = ArgumentParser()
    parser.add_argument(
        "-a", "--api", dest="api", required=True, choices=API_OPTIONS, help="GravityMark graphics API"
    )
    return parser.parse_args()


def get_score(log_path: Path) -> str | None:
    """Parses score value from GravityMark log file"""
    score_pattern = re.compile(r"Score: (\d+)")
    try:
        with log_path.open("r", encoding="utf-8") as file:
            for line in file.readlines():
                match = score_pattern.search(line)
                if match:
                    return match.group(1)
    except OSError:
        return None

    return None


def create_gravitymark_command(gravitymark_path: Path, api: str, image_path: Path):
    """Create the command array for subprocess to run GravityMark"""
    options = [gravitymark_path, api]
    for arg, value in CLI_OPTIONS.items():
        options.append(arg)
        options.append(value)
    options.append("-image")
    options.append(str(image_path))

    return options
