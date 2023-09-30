"""Utility functions for Hitman 3 test script"""
import time
import winreg

import pyautogui as gui


def get_reg(name):
    """Get registry key value"""
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\IO Interactive\HITMAN3",
            0,
            winreg.KEY_READ,
        )
        value, _ = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def get_resolution():
    """Get resolution from registry"""
    width = get_reg("ResolutionWidth")
    height = get_reg("ResolutionHeight")
    return (height, width)


def wait_for_image(img, match_threshold, interval, timeout):
    """Function that will wait for an image to appear on screen. This function will check every
    interval for a match that meets is greater than the match threshold. The function will raise
    an error if the image is not found within the timeout given. Will return the location
    of the image if found
    """
    start_time = time.time()
    current_time = start_time
    while not current_time - start_time > timeout:
        loc = gui.locateOnScreen(img, confidence=match_threshold)
        if loc:
            return loc
        time.sleep(interval)
        current_time = time.time()
    return None
