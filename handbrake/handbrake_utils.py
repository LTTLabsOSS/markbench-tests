"""utility functions for running handbrake tests"""

import os
from pathlib import Path
import time
import shutil

HANDBRAKE_EXECUTABLE = "HandBrakeCLI.exe"
SOURCE_VIDEO_NAME = "big_buck_bunny_1080p24.y4m"
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

from harness_utils.network_share import (
    network_share_auth
)

def handbrake_present() -> bool:
    """Check if handbrake is present on the system"""
    return os.path.isfile(Path(SCRIPT_DIR / HANDBRAKE_EXECUTABLE))


def copy_handbrake_from_network_drive():
    """copy handbrake cli from network drive"""
    source = Path("\\\\Labs\\labs\\01_Installers_Utilities\\Handbrake\\X86\\HandBrakeCLI-1.9.1-win-x86_64\\")
    copy_souce = source / HANDBRAKE_EXECUTABLE
    destination = SCRIPT_DIR / HANDBRAKE_EXECUTABLE
    shutil.copyfile(copy_souce, destination)


def connect_and_copy_handbrake(username, password):
    """Use context manager to connect to network drive and copy handbrake CLI"""
    source = r"H:\01_Installers_Utilities\Handbrake\X86\HandBrakeCLI-1.9.1-win-x86_64\HandBrakeCLI.exe"
    destination = SCRIPT_DIR / HANDBRAKE_EXECUTABLE
    with network_share_auth(r"\\Labs\labs", username, password):
        shutil.copyfile(source, destination)


def is_video_source_present() -> bool:
    """check if big buck bunny video source is present"""
    return os.path.isfile(Path(SCRIPT_DIR / SOURCE_VIDEO_NAME))


def copy_video_source():
    """copy big buck bunny source video to local from network drive"""
    source = r"\\Labs\labs\03_ProcessingFiles\Handbrake Test\big_buck_bunny_1080p24.y4m"
    root_dir = os.path.dirname(os.path.realpath(__file__))
    destination = os.path.join(root_dir, SOURCE_VIDEO_NAME)
    shutil.copyfile(source, destination)


def connect_and_copy_video(username, password):
    """Use context manager to connect to network drive and copy video source"""
    source = r"H:\03_ProcessingFiles\Handbrake Test\big_buck_bunny_1080p24.y4m"
    destination = SCRIPT_DIR / SOURCE_VIDEO_NAME
    with network_share_auth(r"\\Labs\labs", username, password):
        shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
