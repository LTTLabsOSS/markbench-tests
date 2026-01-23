import json
import time

import cv2
import numpy as np
import requests
from mss.windows import MSS as mss

DEFAULT_TIMEOUT = 120.0


class OCRService:
    def __init__(
        self,
        ip_addr: str,
        port: int | str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.ip_addr = ip_addr
        self.port = str(port)
        self.url = f"http://{ip_addr}:{str(port)}/process"
        self.timeout = timeout

    def _query_service(self, word: str, image_bytes):
        try:
            response = requests.post(
                self.url,
                data={"word": word},
                files={"file": ("sc.jpg", image_bytes, "image/jpeg")},
                timeout=self.timeout,
            )

            if not response.ok:
                return None

            if "not found" in response.text:
                return None

            return json.loads(response.text)
        except requests.exceptions.Timeout:
            return None

    def look_for_word(
        self, word: str, attempts: int = 1, interval: float = 0.0
    ) -> bool:
        with mss() as scr:
            monitor_1 = scr.monitors[1]
            for _ in range(attempts):
                sc = np.array(scr.grab(monitor_1))
                _, buf = cv2.imencode(".jpg", sc)
                image_bytes = buf.tobytes()
                result = self._query_service(word, image_bytes)
                if result is not None:
                    return result
                time.sleep(interval)
        return None

    def wait_for_word(self, word: str, interval: float = 0.0, timeout: int = 3) -> bool:
        search_start_time = time.time()
        with mss() as scr:
            monitor_1 = scr.monitors[1]
            while time.time() - search_start_time < timeout:
                sc = np.array(scr.grab(monitor_1))
                _, buf = cv2.imencode(".jpg", sc)
                image_bytes = buf.tobytes()
                result = self._query_service(word, image_bytes)
                if result is not None:
                    return result
                time.sleep(interval)
        return None
