"""Report helpers for harnesses."""

import json
from pathlib import Path


def write_report_json(log_dir: str | Path, report_name: str, report_json: dict) -> None:
    """Write a JSON report to the harness log directory."""
    with Path(log_dir, report_name).open("w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))


def format_resolution(width: int, height: int) -> str:
    """Return a resolution in WxH format."""
    return f"{width}x{height}"


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds."""
    return round(seconds * 1000)
