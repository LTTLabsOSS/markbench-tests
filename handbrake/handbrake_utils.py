"""utility functions for running handbrake tests"""

import os
from pathlib import Path
import time
import shutil

HANDBRAKE_EXECUTABLE = "HandBrakeCLI.exe"
SOURCE_VIDEO_NAME = "big_buck_bunny_1080p24.y4m"
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def handbrake_present() -> bool:
    """Check if handbrake is present on the system"""
    return os.path.isfile(Path(SCRIPT_DIR / HANDBRAKE_EXECUTABLE))


def copy_handbrake_from_network_drive():
    """copy handbrake cli from network drive"""
    source = Path(
        "\\\\labs.lmg.gg\\labs\\01_Installers_Utilities\\Handbrake\\X86\\HandBrakeCLI-1.9.1-win-x86_64\\")
    copy_source = source / HANDBRAKE_EXECUTABLE
    destination = SCRIPT_DIR / HANDBRAKE_EXECUTABLE
    shutil.copyfile(copy_source, destination)


def is_video_source_present() -> bool:
    """check if big buck bunny video source is present"""
    return os.path.isfile(Path(SCRIPT_DIR / SOURCE_VIDEO_NAME))


def copy_video_source():
    """copy big buck bunny source video to local from network drive"""
    source = r"\\labs.lmg.gg\labs\03_ProcessingFiles\Handbrake Test\big_buck_bunny_1080p24.y4m"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, SOURCE_VIDEO_NAME)
    shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
