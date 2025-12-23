
"""utility functions for running ffmpeg tests"""

import os
from pathlib import Path
import time
import shutil

L_FFMPEG_FOLDER = Path("\\\\labs.lmg.gg\\labs\\01_Installers_Utilities\\ffmpeg\\ffmpeg-8.0.1-full_build")
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
FFMPEG_FOLDER_NAME = "ffmpeg-8.0.1-full_build"
FFMPEG_EXE_PATH = SCRIPT_DIR / FFMPEG_FOLDER_NAME / "bin" / "ffmpeg.exe"
SOURCE_VIDEO_NAME = "big_buck_bunny_1080p24.y4m"



def ffmpeg_present() -> bool:
    """Check if ffmpeg is present on the system"""
    return os.path.isfile(FFMPEG_EXE_PATH)


def copy_ffmpeg_from_network_drive():
    """copy ffmpeg cli from network drive"""
    source = L_FFMPEG_FOLDER 
    shutil.copytree(source, SCRIPT_DIR / FFMPEG_FOLDER_NAME)


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

