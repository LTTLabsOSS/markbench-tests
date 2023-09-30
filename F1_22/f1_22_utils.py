"""Utility functions supporting F1 22 test script."""
import os
import re
from argparse import ArgumentParser


def get_resolution() -> tuple[int]:
    """Gets resolution width and height from local xml file created by game."""
    username = os.getlogin()
    config_path = f"C:\\Users\\{username}\\Documents\\My Games\\F1 22\\hardwaresettings"
    config_filename = "hardware_settings_config.xml"
    resolution = re.compile(r"<resolution width=\"(\d+)\" height=\"(\d+)\"")
    cfg = f"{config_path}\\{config_filename}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = resolution.search(line)
            width_match = resolution.search(line)
            if height_match is not None:
                height = height_match.group(2)
            if width_match is not None:
                width = width_match.group(1)
    return (width, height)


def get_args() -> any:
    """Retrieve parsed command line arguments."""
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
