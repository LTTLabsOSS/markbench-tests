"""Utility functions supporting Forza Motorsport test script."""
from argparse import ArgumentParser
import re


def get_resolution(config_file: str) -> tuple[int]:
    """Retrieve the resolution from local configuration files."""
    width_pattern = re.compile(r"\"FullscreenWidth\"=(\d+)")
    height_pattern = re.compile(r"\"FullscreenHeight\"=(\d+)")
    width = 0
    height = 0

    with open(config_file, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            width_match = width_pattern.match(line)
            height_match = height_pattern.match(line)

            if width_match:
                width = width_match.group(1)
            if height_match:
                height = height_match.group(1)

    return (height, width)

def get_args() -> any:
    """Get command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True)
    parser.add_argument(
        "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True)
    return parser.parse_args()


