import pyautogui as gui
import time
import winreg


def get_reg(name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\IO Interactive\HITMAN3', 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def get_resolution():
    width = get_reg("ResolutionWidth")
    height = get_reg("ResolutionHeight")
    return (height, width)


def wait_for_image(img, match_threshold, interval, timeout):
    """Function that will wait for an image to appear on screen. This function will check every
     interval for a match that meets is greater than the match threshold. The function will raise
     an error if the image is not found within the timeout given. Will return the location
     of the image if found"""
    t0 = time.time()
    t1 = t0
    while not t1 - t0 > timeout:
        loc = gui.locateOnScreen(img, confidence=match_threshold)
        if loc:
            return loc
        time.sleep(interval)
        t1 = time.time()
    return None