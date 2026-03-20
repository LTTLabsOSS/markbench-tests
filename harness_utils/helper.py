import logging
import tomllib
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.toml"


@lru_cache(maxsize=1)
def get_ocr_args():
    logging.debug("Checking OCR config path: %s", CONFIG_PATH)

    if CONFIG_PATH.exists():
        logging.debug("Found OCR config file. Using config branch.")
        with CONFIG_PATH.open("rb") as f:
            data = tomllib.load(f)
            ocr = data.get("ocr", {})
            host = str(ocr.get("host", "127.0.0.1"))
            port = str(ocr.get("port", 8000))
            logging.debug(
                "Resolved OCR args from config/defaults: host=%s, port=%s", host, port
            )
            return [host, port]

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
    logging.debug(
        "Resolved OCR args from CLI: host=%s, port=%s", args.keras_host, args.keras_port
    )
    return [str(args.keras_host), str(args.keras_port)]
