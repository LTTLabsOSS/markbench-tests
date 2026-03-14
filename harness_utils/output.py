"""Functions related to logging and formatting output from test harnesses."""

import json
import logging
from pathlib import Path

DEFAULT_LOGGING_FORMAT = "[%(levelname)s] (%(asctime)s) %(message)s"
DEFAULT_DATE_FORMAT = "%H:%M:%S"


def setup_log_directory(log_dir: str | Path) -> None:
    """Creates the log directory for a harness if it does not already exist"""
    Path(log_dir).mkdir(exist_ok=True)


def write_report_json(log_dir: str | Path, report_name: str, report_json: dict) -> None:
    """Writes the json output of a harness to the log directory"""
    with Path(log_dir, report_name).open("w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    """Given width W and height H, return string in format WxH"""
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds"""
    return round((seconds * 1000))


def setup_logging(log_directory: str | Path) -> None:
    """Sets up logging for the harness"""
    setup_log_directory(log_directory)
    log_file = Path(log_directory) / "harness.log"

    logging.basicConfig(
        filename=log_file,
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(
        DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
