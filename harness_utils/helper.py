import logging
import tomllib
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "config.toml"


@lru_cache(maxsize=1)
def get_ocr_args():

    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("rb") as f:
            data = tomllib.load(f)
            ocr = data.get("ocr", {})
            host = str(ocr.get("host", "127.0.0.1"))
            port = str(ocr.get("port", 8000))
            logging.info(
                "Using OCR host from config file: {%s}, port: {%s}", host, port
            )
            return [host, port]

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
    return [str(args.keras_host), str(args.keras_port)]
