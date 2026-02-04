"""Functions related to logging and formatting output from test harnesses."""
import json
import os
import logging
from pathlib import Path

DEFAULT_LOGGING_FORMAT = '[%(levelname)s] [%(filename)s] %(message)s'


def setup_log_directory(log_dir: Path) -> None:
    """Creates the log directory for a harness if it does not already exist"""
    if not log_dir.is_dir():
        Path(log_dir).mkdir()


def write_report_json(
        log_dir: Path, report_json: dict, report_name: str = "report.json") -> None:
    """Writes the json output of a harness to the log directory"""
    with open(os.path.join(log_dir, report_name), "w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    """Given width W and height H, return string in format WxH"""
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds"""
    return round((seconds * 1000))



def setup_logging(log_directory: Path) -> None:
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    setup_log_directory(log_directory)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    if root.handlers:
        return

    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)

    file_handler = logging.FileHandler(f'{log_directory}/harness.log')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)

