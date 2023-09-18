"""DEPRECATED: Utility functions using Open CV"""
from enum import Enum
import logging
import time
import cv2
import pyautogui as gui
import pydirectinput as user
import numpy as np
import imutils

DEFAULT_MATCH_THRESHOLD = 0.8
DEFAULT_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 60  # seconds

templates = {}


class ImageNotFoundTimeout(Exception):
    """Raised when image not found after timeout"""


class ImageNotFound(Exception):
    """Raised when image is not found"""


def get_template(name, aspect="16x9"):
    """Get template image of given aspect ratio"""
    return templates[name][aspect]


def gcd(a, b) -> int:
    """Recursively finds the greatest common divisor of two numbers"""
    return a if b == 0 else gcd(b, a % b)


def aspect_ratio(width, height) -> str:
    """Calculates an aspect ratio given a width and height"""
    denom = int(gcd(width, height))
    x = int(width / denom)
    y = int(height / denom)
    if x == 8 and y == 5:
        return "16x10"
    if x == 16 and y == 9:
        return "16x9"
    return f"{x}x{y}"


# This approach was largely inspired by the article
# https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
def locate_in_image(needle, haystack, threshold=DEFAULT_MATCH_THRESHOLD, debug=0):
    """Tries to find an image template within another image"""
    (template_height, template_width) = needle.shape[:2]

    if debug:
        cv2.imshow("Looking For", needle)
        cv2.waitKey(0)

    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(
            haystack, width=int(haystack.shape[1] * scale), inter=cv2.INTER_NEAREST)
        ratio = haystack.shape[1] / float(resized.shape[1])

        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < template_height or resized.shape[1] < template_width:
            break

        (_, max_val, _, max_loc) = cv2.minMaxLoc(
            cv2.matchTemplate(resized, needle, cv2.TM_CCOEFF_NORMED))

        if debug:
            # draw a bounding box around the detected region
            cv2.rectangle(resized, (max_loc[0], max_loc[1]),
                (max_loc[0] + template_width, max_loc[1] + template_height), (0, 0, 255), 2)
            cv2.imshow("Searching", resized)
            cv2.waitKey(0)

        if max_val >= threshold:
            # compute the (x, y) coordinates of the bounding box based on the resized ratio
            (start_x, start_y) = (int(max_loc[0] * ratio), int(max_loc[1] * ratio))
            (end_x, end_y) = (
                int((max_loc[0] + template_width) * ratio),
                int((max_loc[1] + template_height) * ratio)
            )

            if debug:
                # draw a bounding box around the detected result and display the image
                cv2.rectangle(
                    haystack, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
                cv2.imshow("Found", haystack)
                cv2.waitKey(0)

            return start_x, start_y
    raise ImageNotFound("Image not found on screen")


def locate_on_screen(template_name, threshold=DEFAULT_MATCH_THRESHOLD, debug=0):
    """Tries to find an image template on the screen"""
    screen = gui.screenshot()
    # pyautogui is using Pillow which is giving a format that must be adapted to work with opencv.
    screen = np.array(screen)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    (height, width) = screen.shape[:2]
    ratio = aspect_ratio(width, height)
    needle = get_template(template_name, ratio)
    return needle, locate_in_image(needle, screen, threshold, debug)


def wait_for_image_on_screen(
        template_name, match_threshold=DEFAULT_MATCH_THRESHOLD,
        interval=DEFAULT_INTERVAL,
        timeout=DEFAULT_TIMEOUT):
    """Function that will wait for an image to appear on screen. This function will check every
     interval for a match that meets is greater than the match threshold. The function will raise
     an error if the image is not found within the timeout given. Will return the location
     of the image if found
     """
    start_time = time.time()
    current_time = start_time
    while not current_time - start_time > timeout:
        try:
            img, loc = locate_on_screen(template_name, match_threshold)
            return img, loc
        except ImageNotFound:
            pass
        time.sleep(interval)
        current_time = time.time()
    raise ImageNotFoundTimeout("Could not find image on screen within timeout")


class ClickType(Enum):
    """Enumerates different types of clicks"""
    SINGLE = 0  # uses .click()
    DOUBLE = 1  # uses .doubleclick()
    HARD = 2  # uses mouse.down() and mouse.up()
    AUTO_GUI = 3  # uses pyautogui instead of pydirectinput


def get_middle_of_rect(top_left_corner, height, width) -> tuple[int]:
    """Given x, y coordinates of top left corner of a rectangle and its
    width and height, calculate the coordinates of the center
    """
    center_x = top_left_corner[0] + (width / 2)
    center_y = top_left_corner[1] + (height / 2)
    return int(center_x), int(center_y)  # round to avoid fractional pixels


def wait_and_click(
        template_name, name, click_type: ClickType = ClickType.SINGLE, timeout=DEFAULT_TIMEOUT):
    """Wait to find an given image on screen and then click it"""
    logging.info("Waiting to find and click on %s", name)
    img, img_loc = wait_for_image_on_screen(template_name, timeout=timeout)
    click_loc = get_middle_of_rect(img_loc, img.shape[0], img.shape[1])
    logging.info("Click coordinates %s", (click_loc,))
    if click_type == ClickType.SINGLE:
        user.click(click_loc[0], click_loc[1])
    elif click_type == ClickType.DOUBLE:
        user.doubleClick(click_loc[0], click_loc[1])
    elif click_type == ClickType.HARD:
        user.moveTo(click_loc[0], click_loc[1])
        user.mouseDown()
        user.mouseUp()
    elif click_type == ClickType.AUTO_GUI:
        user.moveTo(click_loc[0], click_loc[1])
        gui.click()
    else:
        raise ValueError("Unknown click type")
