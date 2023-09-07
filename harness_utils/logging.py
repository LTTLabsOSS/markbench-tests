import json
import os

DEFAULT_LOGGING_FORMAT = '%(asctime)s %(levelname)-s %(message)s'
DEFAULT_DATE_FORMAT = '%m-%d %H:%M'

def setup_log_directory(log_dir: str) -> None:
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)


def write_report_json(log_dir: str, report_name: str, report_json: any) -> None:
    with open(os.path.join(log_dir, report_name), "w") as f:
        f.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    return round((seconds * 1000))