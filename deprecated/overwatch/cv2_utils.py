import os
import time
import cv2
import imutils
import numpy as np
import pyautogui as gui

DEFAULT_MATCH_THRESHOLD = 0.8
DEFAULT_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 60  # seconds

# path relative to script
script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
dir16x9 = os.path.join(images_dir, "16x9")
dir16x10 = os.path.join(images_dir, "16x10")

templates = {
    "start_button": {
        "16x10": cv2.imread(os.path.join(dir16x9, "start_room_button.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "start_room_button.png"), cv2.IMREAD_UNCHANGED)
    }
}

class ImageNotFoundTimeout(Exception):
    pass


class ImageNotFound(Exception):
    pass


def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)


def aspect_ratio(w, h):
    """Determines aspect ratio"""
    denom = int(gcd(w, h))
    x = int(w / denom)
    y = int(h / denom)
    if x == 8 and y == 5:
        return "16x10"
    if x == 16 and y == 9:
        return "16x9"


def locate_on_screen(template_name, threshold=DEFAULT_MATCH_THRESHOLD, debug=0):
    """Locates image matching a given template on screen"""
    screen = gui.screenshot()
    # pyautogui is using Pillow which is giving a format that must be adapted to work with opencv.
    screen = np.array(screen)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    (height, width) = screen.shape[:2]
    ratio = aspect_ratio(width, height)
    needle = templates[template_name][ratio]
    return needle, locate_in_image(needle, screen, threshold, debug)


# This approach was largely inspired by the article
# https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
def locate_in_image(needle, haystack, threshold=DEFAULT_MATCH_THRESHOLD, debug=0):
    """Finds an image within image"""
    (tH, tW) = needle.shape[:2]

    if debug:
        cv2.imshow("Looking For", needle)
        cv2.waitKey(0)

    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = imutils.resize(haystack, width=int(haystack.shape[1] * scale), inter=cv2.INTER_NEAREST)
        r = haystack.shape[1] / float(resized.shape[1])

        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        result = cv2.matchTemplate(resized, needle, cv2.TM_CCOEFF_NORMED)
        (_, max_val, _, max_loc) = cv2.minMaxLoc(result)

        if debug:
            # draw a bounding box around the detected region
            # clone = np.dstack([edged, edged, edged])
            cv2.rectangle(resized, (max_loc[0], max_loc[1]),
                          (max_loc[0] + tW, max_loc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Searching", resized)
            cv2.waitKey(0)
            # print(max_val)

        if max_val >= threshold:
            found = (max_val, max_loc, r)

            # unpack the bookkeeping variable and compute the (x, y) coordinates
            # of the bounding box based on the resized ratio
            (_, max_loc, r) = found
            (start_x, start_y) = (int(max_loc[0] * r), int(max_loc[1] * r))
            (end_x, end_y) = (int((max_loc[0] + tW) * r), int((max_loc[1] + tH) * r))

            if debug:
                # draw a bounding box around the detected result and display the image
                cv2.rectangle(haystack, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
                cv2.imshow("Found", haystack)
                cv2.waitKey(0)

            return start_x, start_y
    raise ImageNotFound("Image not found on screen")


def wait_for_image_on_screen(
        template_name, match_threshold=DEFAULT_MATCH_THRESHOLD,
        interval=DEFAULT_INTERVAL,
        timeout=DEFAULT_TIMEOUT):
    """Function that will wait for an image to appear on screen. This function will check every
     interval for a match that meets is greater than the match threshold. The function will raise
     an error if the image is not found within the timeout given. Will return the location
     of the image if found"""
    t0 = time.time()
    t1 = t0
    while not t1 - t0 > timeout:
        try:
            img, loc = locate_on_screen(template_name, match_threshold)
            return img, loc
        except ImageNotFound:
            pass
        time.sleep(interval)
        t1 = time.time()
    raise ImageNotFoundTimeout("Could not find image on screen within timeout")
