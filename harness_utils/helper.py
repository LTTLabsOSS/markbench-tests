import logging
import time
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

import pydirectinput as user
import requests
import tomllib

from harness_utils.screenshot import Screenshotter

user.FAILSAFE = False


@lru_cache(maxsize=1)
def _load_ocr_url():
    config_path = (
        Path(__file__).resolve().parent.parent.parent / "configs" / "config.toml"
    )

    if not config_path.is_file():
        raise FileNotFoundError("config.toml not found")

    with config_path.open("rb") as handle:
        config = tomllib.load(handle)

    host = config["ocr"]["host"]
    port = config["ocr"]["port"]
    if host is None or port is None:
        raise ValueError("config.toml missing host or port")

    url = f"http://{host}:{port}/process"
    return url


def find_word(sc: Screenshotter, word: str, msg: str = "", timeout: int = 3):
    url = _load_ocr_url()

    start_time = time.time()

    while time.time() - start_time < timeout:
        image_bytes = sc.take_sc_bytes()

        try:
            response = requests.post(
                url,
                data={"word": word},
                files={"file": ("sc.jpg", image_bytes, "image/jpeg")},
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"OCR request error: {e}")
            return False

        if not response.ok or "not found" in response.text:
            continue
        else:
            return True

    if msg:
        logging.error(msg)
    else:
        logging.error(f'Did not find: "{word}"')
    return False


def get_ocr_args():
    """helper function to get args for keras"""
    parser = ArgumentParser()
    parser.add_argument(
        "--ocrHost", dest="ocr_host", help="Host for OCR service", required=True
    )
    parser.add_argument(
        "--ocrPort", dest="ocr_port", help="Port for OCR service", required=True
    )
    return parser.parse_args()


def press(keys: str, pause: float = 0.5):
    for part in keys.split(","):
        part = part.strip()
        if not part:
            continue

        if "*" in part:
            key, count = part.split("*", 1)
            key = key.strip()
            count = int(count.strip())
        else:
            key = part
            count = 1

        for _ in range(count):
            user.press(key)
            time.sleep(pause)


def int_time() -> int:
    """Returns the current time in seconds since epoch as an integer"""
    return int(time.time())


def sleep(seconds: int):
    time.sleep(seconds)
