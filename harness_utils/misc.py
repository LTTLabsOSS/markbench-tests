"""Misc utility functions"""
import logging
import os
from pathlib import Path
from zipfile import ZipFile
import time
import pydirectinput as user
import pyautogui as gui
import requests
import vgamepad as vg

class LTTGamePad360(vg.VX360Gamepad):
    """
    Class extension for the virtual game pad library

    Many of the in built functions for this library are super useful but a bit unwieldy to use. 
    This class extension provides some useful functions to make your code look a little cleaner when 
    implemented in our harnesses.
    """
    def single_press(self, button = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, pause = 0.1):
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
    def single_button_press(self, button = vg.DS4_BUTTONS.DS4_BUTTON_CROSS, pause = 0.1):
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

        pause --> the delay between pressing and releasing the button, defaults to 0.1 if not specified
        """

        self.press_button(button=button)
        self.update()
        time.sleep(pause)
        self.release_button(button=button)
        self.update()

    def button_press_n_times(self, button: vg.DS4_BUTTONS, n: int, pause: float):
        """
        Sometimes we need to press a certain gamepad button multiple times in a row, this loop does that for you
        """
        for _ in range(n):
            self.single_button_press(button)
            time.sleep(pause)
    
    def single_dpad_press(self, direction = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH):
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

    def dpad_press_n_times(self, direction: vg.DS4_DPAD_DIRECTIONS, n: int):
        """
        Sometimes we need to press a certain dpad direction multiple times in a row, this loop does that for you
        """
        for _ in range(n):
            self.single_dpad_press(direction)
            time.sleep(0.1)

def clickme(x: int, y: int):
    """Pyautogui's click function sucks, this should do the trick"""
    gui.moveTo(x, y)
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

def mouse_scroll_n_times(n: int, scroll_amount: int, pause: float):
    """
    Pyautogui's mouse scroll function often fails to actually scroll in game menus, this functions solves that problem
    
    n --> the number of times you want to scroll, should be a positive integer
    scroll_amount --> positive is scroll up, negative is scroll down
    pause --> the amount of time to pause betwee subsequent scrolls
    """
    for _ in range(n):
        gui.vscroll(scroll_amount)
        time.sleep(pause)

def press_n_times(key: str, n: int, pause: float):
    """A helper function press the same button multiple times"""
    for _ in range(n):
        user.press(key)
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


def download_file(download_url: str, destination: Path) -> None:
    """Downloads file from given url to destination"""
    response = requests.get(download_url, allow_redirects=True, timeout=120)
    with open(destination, 'wb') as f:
        f.write(response.content)


def extract_archive(zip_file: Path, destination_dir: Path) -> None:
    """Extract all contents of an archive"""
    with ZipFile(zip_file, 'r') as zip_object:
        zip_object.extractall(path=destination_dir)


def extract_file_from_archive(zip_file: Path, member_path: str, destination_dir: Path) -> None:
    """Extract a single file memeber from an archive"""
    with ZipFile(zip_file, 'r') as zip_object:
        zip_object.extract(member_path, path=destination_dir)
