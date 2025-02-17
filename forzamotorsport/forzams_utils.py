"""Utility functions supporting Forza Motorsport test script."""
from argparse import ArgumentParser
import re


def get_resolution(config_file: str) -> tuple[int]:
    """Get resolution from local game file"""
    resolution_pattern = re.compile(r"<option id=\"IDS_Resolution_Label\" value=\"(\d+x\d+)\"/>")
    resolution = 0
    with open(config_file, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            resolution_match = resolution_pattern.search(line)
            if resolution_match is not None:
                resolution = resolution_match.group(1)
    return resolution


def get_args() -> any:
    """Get command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost", dest="keras_host", help="Host for Keras OCR service", required=True)
    parser.add_argument(
        "--kerasPort", dest="keras_port", help="Port for Keras OCR service", required=True)
    return parser.parse_args()