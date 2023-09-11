import json
import logging
import mss
import cv2
import requests
import numpy as np

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class KerasService():
    def __init__(self, ip: str, port: int | str, screenshot_path: str) -> None:
        self.ip = ip
        self.port = str(port)
        self.url = f"http://{ip}:{str(port)}/process"
        self.screenshot_path = screenshot_path

    def _capture_screenshot(self) -> None:
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]  # Identify the display to capture
            screen = np.array(sct.grab(monitor_1))
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(self.screenshot_path, screen)
    
    def _query_service(self, word: str, report_file: any) -> any:
        keras_response = requests.post(self.url, data = {"word": word}, files={"file": report_file})

        if not keras_response.ok:
            return None
        
        if "not found" in keras_response.text:
            return None

        return(json.loads(keras_response.text))

    def capture_screenshot_find_word(self, word: str) -> any:
        self._capture_screenshot()
        with open(self.screenshot_path, "rb") as report_file:
            return self._query_service(word, report_file)