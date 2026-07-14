"""Misc utility functions"""

import json
import logging
import os
import re
import time

import vgamepad as vg


class LTTGamePad360(vg.VX360Gamepad):
    """
    Class extension for the virtual game pad library

    Many of the in built functions for this library are super useful but a bit unwieldy to use.
    This class extension provides some useful functions to make your code look a little cleaner when
    implemented in our harnesses.
    """

    def single_press(self, button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, pause=0.1):
        """
        Custom function to perform a single press of a specified gamepad button

        button --> must be a XUSB_BUTTON class, defaults to dpad down

        Button Options:
        XUSB_GAMEPAD_DPAD_UP
        XUSB_GAMEPAD_DPAD_DOWN
        XUSB_GAMEPAD_DPAD_LEFT
        XUSB_GAMEPAD_DPAD_RIGHT
        XUSB_GAMEPAD_START
        XUSB_GAMEPAD_BACK
        XUSB_GAMEPAD_LEFT_THUMB
        XUSB_GAMEPAD_RIGHT_THUMB
        XUSB_GAMEPAD_LEFT_SHOULDER
        XUSB_GAMEPAD_RIGHT_SHOULDER
        XUSB_GAMEPAD_GUIDE
        XUSB_GAMEPAD_A
        XUSB_GAMEPAD_B
        XUSB_GAMEPAD_X
        XUSB_GAMEPAD_Y

        pause --> the delay between pressing and releasing the button, defaults to 0.1 if not specified
        """

        self.press_button(button=button)
        self.update()
        time.sleep(pause)
        self.release_button(button=button)
        self.update()

    def press_n_times(self, button: vg.XUSB_BUTTON, n: int, pause: float):
        """
        Sometimes we need to press a certain gamepad button multiple times in a row, this loop does that for you
        """
        for _ in range(n):
            self.single_press(button)
            time.sleep(pause)


class LTTGamePadDS4(vg.VDS4Gamepad):
    """
    Class extension for the virtual game pad library

    Many of the in built functions for this library are super useful but a bit unwieldy to use.
    This class extension provides some useful functions to make your code look a little cleaner when
    implemented in our harnesses.
    """

    def single_button_press(
        self, button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS, fastpause=0.05
    ):
        """
        Custom function to perform a single press of a specified gamepad digital button

        button --> must be a DS4_BUTTONS class, defaults to cross

        Button Options:
        DS4_BUTTON_THUMB_RIGHT
        DS4_BUTTON_THUMB_LEFT
        DS4_BUTTON_OPTIONS
        DS4_BUTTON_SHARE
        DS4_BUTTON_TRIGGER_RIGHT
        DS4_BUTTON_TRIGGER_LEFT
        DS4_BUTTON_SHOULDER_RIGHT
        DS4_BUTTON_SHOULDER_LEFT
        DS4_BUTTON_TRIANGLE
        DS4_BUTTON_CIRCLE
        DS4_BUTTON_CROSS
        DS4_BUTTON_SQUARE

        pause --> the delay between pressing and releasing the button, defaults to 0.05 if not specified
        """

        self.press_button(button=button)
        self.update()
        time.sleep(fastpause)
        self.release_button(button=button)
        self.update()

    def button_press_n_times(self, button: vg.DS4_BUTTONS, n: int, pause: float):
        """
        Sometimes we need to press a certain gamepad button multiple times in a row, this loop does that for you
        """
        for _ in range(n):
            self.single_button_press(button)
            time.sleep(pause)

    def single_dpad_press(
        self, direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, pause=0.1
    ):
        """
        Custom function to perform a single press of a specified gamepad button

        button --> must be a DS4_DPAD_DIRECTIONS class, defaults to dpad south

        DPAD Options:
        DS4_BUTTON_DPAD_NONE
        DS4_BUTTON_DPAD_NORTHWEST
        DS4_BUTTON_DPAD_WEST
        DS4_BUTTON_DPAD_SOUTHWEST
        DS4_BUTTON_DPAD_SOUTH
        DS4_BUTTON_DPAD_SOUTHEAST
        DS4_BUTTON_DPAD_EAST
        DS4_BUTTON_DPAD_NORTHEAST
        DS4_BUTTON_DPAD_NORTH

        pause --> the delay between pressing and releasing the button, defaults to 0.1 if not specified
        """

        self.directional_pad(direction=direction)
        self.update()
        time.sleep(pause)
        self.reset()
        self.update()

    def dpad_press_n_times(
        self, direction: vg.DS4_DPAD_DIRECTIONS, n: int, pause: float
    ):
        """
        Sometimes we need to press a certain dpad direction multiple times in a row, this loop does that for you
        """
        for _ in range(n):
            self.single_dpad_press(direction)
            time.sleep(pause)


def remove_files(paths: list[str]) -> None:
    """Removes files specified by provided list of file paths.
    Does nothing for a path that does not exist.
    """
    for path in paths:
        try:
            os.remove(path)
            logging.info("Removed file: %s", path)
        except FileNotFoundError:
            logging.info("File already removed: %s", path)


def find_eg_game_version(gamefoldername: str) -> str | None:
    """Find the version of the specific game (e.g., AlanWake2) from the launcher installed data."""
    installerdat = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"

    try:
        # Open the file and read its entire content
        with open(installerdat, encoding="utf-8") as file:
            file_content = file.read()

        # Check if the "InstallationList" section is in the content
        installation_list_match = re.search(
            r'"InstallationList":\s*(\[[^\]]*\])', file_content
        )
        if not installation_list_match:
            print("No InstallationList found.")
            return None

        # Extract the InstallationList part from the file
        installation_list_json = installation_list_match.group(1)

        # Load the installation list as JSON
        installation_list = json.loads(installation_list_json)

        # Loop through each item in the installation list
        for game in installation_list:
            # Check if the game's InstallLocation contains the target string (AlanWake2)
            if gamefoldername in game.get("InstallLocation", ""):
                # Return the AppVersion for this game
                return game.get("AppVersion", None)

    except Exception as e:
        print(f"Error: {e}")

    return None
