"""Allows accessing Keras Service if available."""
import io
import json
import logging
import time
import mss
import cv2
import requests
import numpy as np
from enum import Enum
from dataclasses import dataclass

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

DEFAULT_TIMEOUT = 120.0


class ScreenShotDivideMethod(Enum):
    """split method"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    QUADRANT = "quadrant"
    NONE = "none"


class ScreenShotQuadrant(Enum):
    """split arguments"""
    TOP = 1
    BOTTOM = 2
    LEFT = 1
    RIGHT = 2
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class FrameDivideException(ValueError):
    """Exception indicating was encountered while trying to divide a frame"""


@dataclass
class ScreenSplitConfig:
    """data class to contain config for taking splitting a screen shot"""
    divide_method: ScreenShotDivideMethod
    quadrant: ScreenShotQuadrant


class KerasService():
    """Sets up connection to a Keras service and provides methods to use it"""

    def __init__(
            self,
            ip_addr: str,
            port: int | str,
            timeout: float = DEFAULT_TIMEOUT) -> None:
        self.ip_addr = ip_addr
        self.port = str(port)
        self.url = f"http://{ip_addr}:{str(port)}/process"
        self.timeout = timeout

    def _capture_screenshot(self, split_config: ScreenSplitConfig) -> io.BytesIO:
        screenshot = None
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]  # Identify the display to capture
            screenshot = np.array(sct.grab(monitor_1))
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

        if split_config.divide_method == ScreenShotDivideMethod.HORIZONTAL:
            screenshot = self._divide_horizontal(screenshot, split_config.quadrant)
        elif split_config.divide_method == ScreenShotDivideMethod.VERTICAL:
            screenshot = self._divide_vertical(screenshot, split_config.quadrant)
        elif split_config.divide_method == ScreenShotDivideMethod.QUADRANT:
            screenshot = self._divide_in_four(screenshot, split_config.quadrant)

        _, encoded_image = cv2.imencode('.jpg', screenshot)
        return io.BytesIO(encoded_image)

    def _query_service(self, word: str, image_bytes: io.BytesIO) -> any:
        try:
            keras_response = requests.post(
                self.url,
                data={"word": word},
                files={"file": image_bytes},
                timeout=self.timeout
            )

            if not keras_response.ok:
                return None

            if "not found" in keras_response.text:
                return None

            return json.loads(keras_response.text)
        except requests.exceptions.Timeout:
            return None

    def _divide_horizontal(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot horizontally"""
        height, _, _ = screenshot.shape
        if quadrant == ScreenShotQuadrant.TOP:
            return screenshot[0:int(height/2), :]
        if quadrant == ScreenShotQuadrant.BOTTOM:
            return screenshot[int(height/2):int(height), :]
        raise FrameDivideException(
            f"Unrecognized quadrant for horizontal: {quadrant}")

    def _divide_vertical(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot vertically"""
        _, width, _ = screenshot.shape
        if quadrant == quadrant.LEFT:
            return screenshot[:, 0:int(width/2)]
        if quadrant == quadrant.RIGHT:
            return screenshot[:, int(width/2):int(width)]
        raise FrameDivideException(
                f"Unrecognized quadrant for vertical: {quadrant}")

    def _divide_in_four(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot in four quadrants"""
        height, width, _ = screenshot.shape
        if quadrant == ScreenShotQuadrant.TOP_LEFT:
            return screenshot[0:int(height/2), 0:int(width/2)]
        if quadrant == ScreenShotQuadrant.TOP_RIGHT:
            return screenshot[0:int(height/2), int(width/2):int(width)]
        if quadrant == ScreenShotQuadrant.BOTTOM_LEFT:
            return screenshot[int(height/2):int(height), 0:int(width/2)]
        if quadrant == ScreenShotQuadrant.BOTTOM_RIGHT:
            return screenshot[int(height/2):int(height), int(width/2):int(width)]
        raise FrameDivideException(
            f"Unrecognized quadrant for in four: {quadrant}")

    def _look_for_word(
            self, word: str,
            attempts: int = 1,
            interval: float = 0.0,
            split_config: ScreenSplitConfig = None) -> bool:
        """implementation of look for word"""
        for _ in range(attempts):
            image_bytes = self._capture_screenshot(split_config)
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None

    def look_for_word(self, word: str, attempts: int = 1, interval: float = 0.0) -> bool:
        """Takes a screenshot of the monitor and searches for a given word.
        Will look for the word at a given time interval until the specified number
        of attempts is reached.
        Will return early if the query result comes back with a match.
        """
        empty_config = ScreenSplitConfig(divide_method=ScreenShotDivideMethod.NONE, quadrant=ScreenShotQuadrant.TOP)
        return self._look_for_word(word, attempts, interval, empty_config)

    def look_for_word(self, word: str, attempts: int = 1, interval: float = 0.0, split_config: ScreenSplitConfig = None) -> bool:
        """Overload for look_for_word but allows for screen splitting
        which will look for a word in only part of the screen
        """
        return self._look_for_word(word, attempts, interval, split_config)

    def _wait_for_word(
            self,
            word: str,
            interval: float,
            timeout: float,
            split_config: ScreenSplitConfig) -> bool:
        """implementation of wait for word"""
        search_start_time = time.time()
        while time.time() - search_start_time < timeout:
            image_bytes = self._capture_screenshot(split_config)
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None

    def wait_for_word(self, word: str, interval: float = 0.0, timeout: float = 0.0) -> bool:
        """Takes a screenshot of the monitor and searches for a given word.
        Will look for the word at a given time interval until the specified timeout
        has been exceeded.
        Will return early if the query result comes back with a match.
        """
        empty_config = ScreenSplitConfig(divide_method=ScreenShotDivideMethod.NONE, quadrant=ScreenShotQuadrant.TOP)
        return self._wait_for_word(word, interval, timeout, empty_config)

    def wait_for_word(self, word: str, interval: float = 0.0, timeout: float = 0.0, split_config: ScreenSplitConfig = None) -> bool:
        """Overload for wait_for_word but allows for screen splitting
        which will look for a word in only part of the screen
        """
        return self._wait_for_word(word, interval, timeout, split_config)
