"""Utility functions supporting Returnal test script."""
import os
import re
from argparse import ArgumentParser


def get_resolution(config_path: str) -> tuple[int]:
    """Retrieve the resolution from local configuration files."""
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width = 0
    height = 0

    with open(config_path, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            width_match = width_pattern.match(line)
            height_match = height_pattern.match(line)

            if width_match:
                width = width_match.group(1)
            if height_match:
                height = height_match.group(1)

    return (height, width)


def remove_intro_videos(file_paths: list[str]) -> None:
    """Removes given video file paths"""
    for video in file_paths:
        try:
            os.remove(video)
        except FileNotFoundError:
            # If file not found, it has likely already been deleted before.
            pass


def get_args() -> any:
    """Get command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost",
        dest="keras_host",
        help="Host for Keras OCR service",
        required=True,
    )
    parser.add_argument(
        "--kerasPort",
        dest="keras_port",
        help="Port for Keras OCR service",
        required=True,
    )
    return parser.parse_args()
