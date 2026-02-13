"""Utility functions supporting Returnal test script."""
import re


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

