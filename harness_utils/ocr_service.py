import json
import logging
import tomllib
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path
from time import monotonic, sleep
from typing import Any

import requests

from harness_utils.screenshot import capture_screenshot_jpg_bytes

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.toml"
OCR_REQUEST_TIMEOUT = 5
FAILED_RUN = (0, 0)


@lru_cache(maxsize=1)
def get_ocr_url(
    ip_addr: str | None = None,
    port: int | str | None = None,
) -> str:
    host = "127.0.0.1"
    ocr_port = "8000"

    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("rb") as f:
            data = tomllib.load(f)
            ocr = data.get("ocr", {})
            host = str(ocr.get("host", host))
            ocr_port = str(ocr.get("port", ocr_port))
        logging.debug("Found OCR config file. Using config/default values.")
    else:
        logging.debug(
            "OCR config file not found. Using defaults unless CLI overrides exist."
        )
        parser = ArgumentParser(add_help=False)
        parser.add_argument("--ocrHost", dest="ocr_host")
        parser.add_argument("--ocrPort", dest="ocr_port")
        args, _ = parser.parse_known_args()
        host = str(args.ocr_host or host)
        ocr_port = str(args.ocr_port or ocr_port)

    host = str(ip_addr) if ip_addr is not None else host
    ocr_port = str(port) if port is not None else ocr_port
    logging.debug("Resolved OCR url: host=%s, port=%s", host, ocr_port)
    return f"http://{host}:{ocr_port}/process"


def _query_ocr_service(word: str, vulkan: bool = False, crop: str | None = None) -> Any:
    image_bytes = capture_screenshot_jpg_bytes(vulkan, crop)
    if image_bytes is None:
        return None

    url = get_ocr_url()
    try:
        response = requests.post(
            url,
            data={"word": word},
            files={"file": image_bytes},
            timeout=OCR_REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout as exc:
        logging.warning(
            "OCR service timed out after %ss while searching for word=%r url=%s error=%s",
            OCR_REQUEST_TIMEOUT,
            word,
            url,
            exc,
        )
        return None
    except requests.exceptions.ConnectionError as exc:
        logging.warning(
            "OCR service connection failed while searching for word=%r url=%s error=%s",
            word,
            url,
            exc,
        )
        return None
    except requests.exceptions.RequestException as exc:
        logging.warning(
            "OCR service request failed while searching for word=%r url=%s error=%s",
            word,
            url,
            exc,
        )
        return None

    if not response.ok or "not found" in response.text:
        return None

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as exc:
        logging.warning(
            "OCR service returned invalid JSON while searching for word=%r url=%s error=%s",
            word,
            url,
            exc,
        )
        return None


def find_word(
    word: str,
    vulkan: bool = False,
    interval: float = 0,
    timeout: int = 0,
    msg: str | None = None,
    crop: str | None = None,
):
    logging.debug("Searching OCR word=%r timeout=%s", word, timeout)
    start_time = monotonic()
    while True:
        result = _query_ocr_service(word, vulkan, crop)
        elapsed_time = monotonic() - start_time
        if result is not None:
            logging.debug(
                "Found OCR word=%r elapsed=%.2fs result=%s", word, elapsed_time, result
            )
            return result
        if elapsed_time > timeout:
            logging.debug(msg or f"OCR did not find word={word!r} timeout={timeout}s")
            return None
        sleep(interval)
