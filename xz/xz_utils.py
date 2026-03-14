"""utility functions for xz test script"""

import os
from pathlib import Path
import time
import shutil

XZ_EXECUTABLE = "xz_5.6.2_x86_64.exe"
SCRIPT_DIRECTORY = Path(__file__).resolve().parent


def xz_executable_exists() -> bool:
    """Check if xz has been downloaded or not"""
    return (SCRIPT_DIRECTORY / XZ_EXECUTABLE).is_file()


def copy_from_network_drive():
    """Download xz from network drive"""
    source = r"\\labs.lmg.gg\labs\01_Installers_Utilities\xz\xz_5.6.2_x86_64.exe"
    destination = SCRIPT_DIRECTORY / XZ_EXECUTABLE
    shutil.copyfile(source, destination)

    source = r"\\labs.lmg.gg\labs\03_ProcessingFiles\Compression\tq_dlss_explained_1080p.mp4"
    destination = SCRIPT_DIRECTORY / "tq_dlss_explained_1080p.mp4"
    shutil.copyfile(source, destination)


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
