"""Allows accessing Keras Service if available."""

import io
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum

import cv2
import requests

from harness_utils.screenshot import capture_screenshot_array

logger = logging.getLogger(__name__)
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


class KerasService:
    """Sets up connection to a Keras service and provides methods to use it"""

    def __init__(
        self, ip_addr: str, port: int | str, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        self.ip_addr = ip_addr
        self.port = str(port)
        self.url = f"http://{ip_addr}:{str(port)}/process"
        self.timeout = timeout

    def _apply_split_config(self, screenshot, split_config: ScreenSplitConfig):
        if split_config.divide_method == ScreenShotDivideMethod.HORIZONTAL:
            return self._divide_horizontal(screenshot, split_config.quadrant)
        if split_config.divide_method == ScreenShotDivideMethod.VERTICAL:
            return self._divide_vertical(screenshot, split_config.quadrant)
        if split_config.divide_method == ScreenShotDivideMethod.QUADRANT:
            return self._divide_in_four(screenshot, split_config.quadrant)
        return screenshot

    def _capture_screenshot(self, split_config) -> io.BytesIO:
        logger.info("Capturing Keras screenshot split_config=%s", split_config)
        screenshot = capture_screenshot_array()
        if split_config is not None:
            screenshot = self._apply_split_config(screenshot, split_config)
        _, encoded_image = cv2.imencode(".jpg", screenshot)
        return io.BytesIO(encoded_image)

    def _capture_vulkan_screenshot(self, split_config):
        """Capture a screenshot from Vulkan fullscreen using DXGI Desktop Duplication"""
        logger.info("Capturing Keras Vulkan screenshot split_config=%s", split_config)

        screenshot = capture_screenshot_array(vulkan=True)
        if screenshot is None:
            print("Failed to capture Vulkan frame.")
            return None
        if split_config is not None:
            screenshot = self._apply_split_config(screenshot, split_config)
        _, encoded_image = cv2.imencode(".jpg", screenshot)
        return io.BytesIO(encoded_image)

    def _query_service(self, word: str, image_bytes: io.BytesIO | None):
        logger.info("Querying Keras service word=%s url=%s", word, self.url)
        if image_bytes is None:
            logger.info("No image bytes provided, skipping query")
            return None
        try:
            keras_response = requests.post(
                self.url,
                data={"word": word},
                files={"file": image_bytes},
                timeout=self.timeout,
            )

            if not keras_response.ok:
                logger.warning(
                    "Keras service returned non-OK response status=%s",
                    keras_response.status_code,
                )
                return None

            if "not found" in keras_response.text:
                logger.info("Keras service did not find word=%s", word)
                return None

            logger.info("Keras service found word=%s", word)
            return json.loads(keras_response.text)
        except requests.exceptions.Timeout:
            logger.warning(
                "Keras service timed out word=%s timeout=%s", word, self.timeout
            )
            return None

    def _divide_horizontal(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot horizontally"""
        height, _ = screenshot.shape
        if quadrant == ScreenShotQuadrant.TOP:
            return screenshot[0 : int(height / 2), :]
        if quadrant == ScreenShotQuadrant.BOTTOM:
            return screenshot[int(height / 2) : int(height), :]
        raise FrameDivideException(f"Unrecognized quadrant for horizontal: {quadrant}")

    def _divide_vertical(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot vertically"""
        _, width = screenshot.shape
        if quadrant == quadrant.LEFT:
            return screenshot[:, 0 : int(width / 2)]
        if quadrant == quadrant.RIGHT:
            return screenshot[:, int(width / 2) : int(width)]
        raise FrameDivideException(f"Unrecognized quadrant for vertical: {quadrant}")

    def _divide_in_four(self, screenshot, quadrant: ScreenShotQuadrant):
        """divide the screenshot in four quadrants"""
        height, width = screenshot.shape
        if quadrant == ScreenShotQuadrant.TOP_LEFT:
            return screenshot[0 : int(height / 2), 0 : int(width / 2)]
        if quadrant == ScreenShotQuadrant.TOP_RIGHT:
            return screenshot[0 : int(height / 2), int(width / 2) : int(width)]
        if quadrant == ScreenShotQuadrant.BOTTOM_LEFT:
            return screenshot[int(height / 2) : int(height), 0 : int(width / 2)]
        if quadrant == ScreenShotQuadrant.BOTTOM_RIGHT:
            return screenshot[
                int(height / 2) : int(height), int(width / 2) : int(width)
            ]
        raise FrameDivideException(f"Unrecognized quadrant for in four: {quadrant}")

    def wait_for_word(
        self,
        word: str,
        interval: float = 0.0,
        timeout: float = 0.0,
        split_config: ScreenSplitConfig | None = None,
    ):
        """Takes a screenshot of the monitor and searches for a given word.
        Will look for the word at a given time interval until the specified timeout
        has been exceeded.
        Will return early if the query result comes back with a match.
        """

        search_start_time = time.time()
        while time.time() - search_start_time < timeout:
            logger.info("Waiting for word attempt word=%s timeout=%s", word, timeout)
            image_bytes = self._capture_screenshot(split_config)
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None

    def wait_for_word_vulkan(
        self,
        word: str,
        interval: float = 0.0,
        timeout: float = 0.0,
        split_config: ScreenSplitConfig | None = None,
    ):
        """Overload for wait_for_word but captures Vulkan frames"""
        search_start_time = time.time()
        while time.time() - search_start_time < timeout:
            logger.info(
                "Waiting for word with Vulkan attempt word=%s timeout=%s", word, timeout
            )
            image_bytes = self._capture_vulkan_screenshot(split_config)
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None
