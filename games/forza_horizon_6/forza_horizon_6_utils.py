"""Utility functions for Forza Horizon 6 test script"""

import re
from pathlib import Path


def read_resolution(config_path: str | Path) -> tuple[int, int]:
    """Gets the resolution from local file"""
    height_pattern = re.compile(r"<ResolutionHeight value=\"(\d+)\"/>")
    width_pattern = re.compile(r"<ResolutionWidth value=\"(\d+)\"/>")
    width = 0
    height = 0
    with open(config_path, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = int(height_match.group(1))
            if width_match is not None:
                width = int(width_match.group(1))
    return (width, height)
