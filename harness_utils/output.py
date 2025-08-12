"""Functions related to logging and formatting output from test harnesses."""
import json
import os
import logging

DEFAULT_LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
DEFAULT_DATE_FORMAT = '%m-%d %H:%M'


def setup_log_directory(log_dir: str) -> None:
    """Creates the log directory for a harness if it does not already exist"""
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


# change in future, this any bothers me, should be dict
def write_report_json(
        log_dir: str, report_name: str, report_json: dict) -> None:
    """Writes the json output of a harness to the log directory"""
    with open(os.path.join(log_dir, report_name), "w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    """Given width W and height H, return string in format WxH"""
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds"""
    return round((seconds * 1000))


def setup_logging(log_directory: str) -> None:
    """Sets up logging for the harness"""
    setup_log_directory(log_directory)

    logging.basicConfig(filename=f'{log_directory}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
