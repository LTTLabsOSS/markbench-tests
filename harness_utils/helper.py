import logging
import tomllib
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "config.toml"


def get_ocr_args():
    cache_before = _get_ocr_args_cached.cache_info()
    logging.info(
        "get_ocr_args called. Cache state before lookup: hits=%s, misses=%s, currsize=%s",
        cache_before.hits,
        cache_before.misses,
        cache_before.currsize,
    )
    result = _get_ocr_args_cached()
    cache_after = _get_ocr_args_cached.cache_info()

    if cache_after.hits > cache_before.hits:
        logging.info(
            "Returning cached OCR args: host=%s, port=%s", result[0], result[1]
        )
    else:
        logging.info(
            "Returning freshly resolved OCR args: host=%s, port=%s",
            result[0],
            result[1],
        )

    return result


@lru_cache(maxsize=1)
def _get_ocr_args_cached():
    logging.info("Resolving OCR args for the first time.")
    logging.info("Computed OCR config path: %s", CONFIG_PATH)
    logging.info("Checking whether OCR config path exists.")

    if CONFIG_PATH.exists():
        logging.info("OCR config file found at: %s", CONFIG_PATH)
        logging.info("Opening OCR config file for reading.")
        try:
            with CONFIG_PATH.open("rb") as f:
                data = tomllib.load(f)
        except Exception:
            logging.exception("Failed to load OCR config file from: %s", CONFIG_PATH)
            raise

        logging.info("OCR config file loaded successfully.")
        logging.info("Top-level config keys present: %s", list(data.keys()))
        ocr = data.get("ocr", {})
        logging.info(
            "Resolved 'ocr' section from config with type: %s", type(ocr).__name__
        )

        if "ocr" not in data:
            logging.info(
                "No 'ocr' section found in config. Falling back to default OCR host and port values."
            )
        else:
            logging.info("Using 'ocr' section from config file.")

        raw_host = ocr.get("host", "127.0.0.1")
        raw_port = ocr.get("port", 8000)

        if "host" in ocr:
            logging.info("Found OCR host in config: %s", raw_host)
        else:
            logging.info("OCR host missing in config. Using default host: 127.0.0.1")

        if "port" in ocr:
            logging.info("Found OCR port in config: %s", raw_port)
        else:
            logging.info("OCR port missing in config. Using default port: 8000")

        host = str(raw_host)
        port = str(raw_port)
        logging.info(
            "Using OCR args from config/defaults: host=%s, port=%s", host, port
        )
        return [host, port]

    logging.warning("OCR config file not found at: %s", CONFIG_PATH)
    logging.warning(
        "Falling back to command-line arguments '--kerasHost' and '--kerasPort'."
    )

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
    logging.info("Parsing OCR host and port from command-line arguments.")
    args = parser.parse_args()
    host = str(args.keras_host)
    port = str(args.keras_port)
    logging.info(
        "Using OCR args from command-line arguments: host=%s, port=%s", host, port
    )
    return [host, port]
