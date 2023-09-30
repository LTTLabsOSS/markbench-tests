"""Utility functions supporting RDR2 test script."""
import getpass
import pathlib
import re


def get_resolution() -> tuple[int]:
    """Gets resolution width and height from local xml file created by game."""
    # C:\Users\User\Documents\Rockstar Games\Red Dead Redemption 2\Settings\system.xml"
    path = pathlib.Path(
        "C:/Users/",
        getpass.getuser(),
        "Documents",
        "Rockstar Games",
        "Red Dead Redemption 2",
        "Settings",
        "system.xml",
    )
    width = "0"
    height = "0"

    screen_width = re.compile(r"<screenWidth value=\"(\d+)\" />")
    screen_height = re.compile(r"<screenHeight value=\"(\d+)\" />")

    try:
        with open(path, encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                width_match = screen_width.search(line)
                height_match = screen_height.search(line)
                if width_match is not None:
                    width = width_match.group(1)
                if height_match is not None:
                    height = height_match.group(1)
    except OSError:
        width = "0"
        height = "0"

    return (width, height)
