"""Allows accessing Keras Service if available."""
import json
import logging
import time
import mss
import cv2
import requests
import numpy as np

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

DEFAULT_TIMEOUT = 120.0

class KerasService():
    """Sets up connection to a Keras serivce and provides methods to use it"""
    def __init__(
            self,
            ip_addr: str,
            port: int | str,
            screenshot_path: str,
            timeout: float = DEFAULT_TIMEOUT) -> None:
        self.ip_addr = ip_addr
        self.port = str(port)
        self.url = f"http://{ip_addr}:{str(port)}/process"
        self.screenshot_path = screenshot_path
        self.timeout = timeout

    def _capture_screenshot(self) -> None:
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]  # Identify the display to capture
            screen = np.array(sct.grab(monitor_1))
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(self.screenshot_path, screen)

    def _query_service(self, word: str, report_file: any) -> any:
        try:
            keras_response = requests.post(
                self.url,
                data={"word": word},
                files={"file": report_file},
                timeout=self.timeout
            )

            if not keras_response.ok:
                return None

            if "not found" in keras_response.text:
                return None

            return json.loads(keras_response.text)
        except requests.exceptions.Timeout:
            return None

    def capture_screenshot_find_word(self, word: str) -> any:
        """Take a screenshot and try to find the given word within it."""
        self._capture_screenshot()
        with open(self.screenshot_path, "rb") as report_file:
            return self._query_service(word, report_file)

    def look_for_word(self, word: str, attempts: int = 1, interval: float = 0.0) -> bool:
        """Takes a screenshot of the monitor and searches for a given word.
        Will look for the word at a given time interval until the specified number
        of attempts is reached.
        Will return early if the query result comes back with a match.
        """
        for _ in range(attempts):
            result = self.capture_screenshot_find_word(word)
            if result is not None:
                return result
            time.sleep(interval)
        return None

    def wait_for_word(self, word: str, interval: float = 0.0, timeout: float = 0.0):
        """Takes a screenshot of the monitor and searches for a given word.
        Will look for the word at a given time interval until the specified timeout
        has been exceeded.
        Will return early if the query result comes back with a match.
        """
        search_start_time = time.time()
        while time.time() - search_start_time < timeout:
            result = self.capture_screenshot_find_word(word)
            if result is not None:
                return result
            time.sleep(interval)
        return None
