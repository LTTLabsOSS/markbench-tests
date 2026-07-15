"""utility functions for running ffmpeg tests"""

import shutil
import time
import subprocess
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parent

TEST_OPTIONS = {
    "x86_64": {
        "folder": "ffmpeg-8.0.1-full_build",
        "network_path": Path(
            r"\\labs.lmg.gg\labs\01_Installers_Utilities\ffmpeg\ffmpeg-8.0.1-full_build"
        ),
    },
    "arm64": {
        "folder": "ffmpeg-8.0.1-full_static-win-arm64",
        "network_path": Path(
            r"\\labs.lmg.gg\labs\01_Installers_Utilities\ffmpeg\ffmpeg-8.0.1-full_static-win-arm64"
        ),
    },
}

SOURCE_VIDEO_NAME = "big_buck_bunny_1080p24.y4m"

#Helpers
def get_ffmpeg_root(architecture: str) -> Path:
    """Return local FFmpeg folder root for architecture"""
    return SCRIPT_DIRECTORY / TEST_OPTIONS[architecture]["folder"]


def get_ffmpeg_exe_path(architecture: str) -> Path:
    """Return full path to ffmpeg.exe for architecture"""
    return get_ffmpeg_root(architecture) / "bin" / "ffmpeg.exe"


def get_network_ffmpeg_path(architecture: str) -> Path:
    """Return network path for FFmpeg build"""
    return TEST_OPTIONS[architecture]["network_path"]

#Checks and Copies
def ffmpeg_present(architecture: str) -> bool:
    """Check if ffmpeg exists locally for architecture"""
    return get_ffmpeg_exe_path(architecture).is_file()


def copy_ffmpeg_from_network_drive(architecture: str):
    """Copy FFmpeg build from network share"""
    source = get_network_ffmpeg_path(architecture)
    destination = get_ffmpeg_root(architecture)

    if destination.exists() and (destination / "bin" / "ffmpeg.exe").exists():
        return

    shutil.copytree(source, destination)


def is_video_source_present() -> bool:
    """check if big buck bunny video source is present"""
    return (SCRIPT_DIRECTORY / SOURCE_VIDEO_NAME).is_file()


def copy_video_source():
    """copy big buck bunny source video to local from network drive"""
    source = r"\\labs.lmg.gg\labs\03_ProcessingFiles\Handbrake Test\big_buck_bunny_1080p24.y4m"
    destination = SCRIPT_DIRECTORY / SOURCE_VIDEO_NAME
    shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)

def vmaf_supported(architecture: str) -> bool:
    """Determine if VMAF can run in this environment"""
    try:
        ffmpeg_exe = get_ffmpeg_exe_path(architecture)

        result = subprocess.run(
            [str(ffmpeg_exe), "-filters"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return "libvmaf" in output.lower()
    except Exception:
        return False
