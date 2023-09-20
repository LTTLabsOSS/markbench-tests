"""Functions related to logging and formatting output from test harnesses."""
import json
import os

DEFAULT_LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
DEFAULT_DATE_FORMAT = '%m-%d %H:%M'

def setup_log_directory(log_dir: str) -> None:
    """Creates the log directory for a harness if it does not already exist"""
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


def write_report_json(log_dir: str, report_name: str, report_json: any) -> None:
    """Writes the json output of a harness to the log directory"""
    with open(os.path.join(log_dir, report_name), "w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    """Given width W and height H, return string in format WxH"""
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds"""
    return round((seconds * 1000))
