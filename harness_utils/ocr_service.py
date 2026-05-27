import json
import logging
import tomllib
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path
from time import monotonic, sleep
from typing import Any

import pydirectinput as user
import requests

from harness_utils.screenshot import capture_screenshot_jpg_bytes

user.FAILSAFE = False

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
        logging.debug("OCR config file not found. Falling back to CLI args.")
        parser = ArgumentParser()
        parser.add_argument(
            "--kerasHost",
            dest="keras_host",
            help="Host for Keras OCR service",
            required=True,
        )
        parser.add_argument(
            "--kerasPort",
            dest="keras_port",
            help="Port for Keras OCR service",
            required=True,
        )
        args = parser.parse_args()
        host = str(args.keras_host)
        ocr_port = str(args.keras_port)

    host = str(ip_addr) if ip_addr is not None else host
    ocr_port = str(port) if port is not None else ocr_port
    logging.debug("Resolved OCR url: host=%s, port=%s", host, ocr_port)
    return f"http://{host}:{ocr_port}/process"


def _capture_screen_bytes(vulkan: bool = False):
    return capture_screenshot_jpg_bytes(vulkan)


def _query_ocr_service(word: str, vulkan: bool = False) -> Any:

    image_bytes = _capture_screen_bytes(vulkan)
    if image_bytes is None:
        return None

    response = requests.post(
        get_ocr_url(),
        data={"word": word},
        files={"file": image_bytes},
        timeout=OCR_REQUEST_TIMEOUT,
    )

    if not response.ok or "not found" in response.text:
        return None

    return json.loads(response.text)


def find_word(
    word: str,
    vulkan: bool = False,
    interval: int = 0,
    timeout: int = 0,
    msg: str | None = None,
):
    start_time = monotonic()
    while True:
        result = _query_ocr_service(word, vulkan)
        if result is not None:
            logging.debug(str(result))
            return result
        if monotonic() > start_time + timeout:
            logging.info(msg or f"did not find {word} in {timeout}s")
            return None
        sleep(interval)


def press(sequence: str, pause: float = 0.3) -> None:
    """Press keys described by a comma-separated sequence like ``up*2, down*3``."""
    steps = [step.strip() for step in sequence.split(",")]

    for step in steps:
        if not step:
            continue

        key, separator, count_text = step.partition("*")
        key = key.strip()
        if not key:
            continue

        count = 1
        if separator:
            count_text = count_text.strip()
            if not count_text:
                logging.warning(
                    "Skipping press step with missing repeat count: %r", step
                )
                continue
            if not count_text.isdigit():
                logging.warning(
                    "Skipping press step with invalid repeat count: %r", step
                )
                continue
            count = int(count_text)
            if count < 1:
                logging.warning(
                    "Skipping press step with non-positive repeat count: %r", step
                )
                continue

        user.press(key, presses=count, interval=pause)
