
import json
import time
import requests

from harness_utils.screenshot import Screenshotter

DEFAULT_TIMEOUT = 120.0

class OcrService():

    def __init__(
            self,
            ip_addr: str,
            port: int | str,
            screenshotter: Screenshotter,
            timeout: float = DEFAULT_TIMEOUT) -> None:
        self.ip_addr = ip_addr
        self.port = str(port)
        self.url = f"http://{ip_addr}:{str(port)}/process"
        self.timeout = timeout
        self.screenshotter = screenshotter

    def _query_service(self, word: str, image_bytes):
        try:
            response = requests.post(
                self.url,
                data={"word": word},
                files={"file": ("sc.jpg", image_bytes, "image/jpeg")},
                timeout=self.timeout
            )

            if not response.ok:
                return None

            if "not found" in response.text:
                return None

            return json.loads(response.text)
        except requests.exceptions.Timeout:
            return None


    def look_for_word(self, word: str, attempts: int = 1, interval: float = 0.0 ) -> bool:
        for _ in range(attempts):
            image_bytes = self.screenshotter.take_sc_bytes()
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None
    


    def wait_for_word(self, word: str, interval: float = 0.0, timeout: float = 0.0) -> bool:
        search_start_time = time.time()
        while time.time() - search_start_time < timeout:
            image_bytes = self.screenshotter.take_sc_bytes()
            result = self._query_service(word, image_bytes)
            if result is not None:
                return result
            time.sleep(interval)
        return None
