"""Report-writing helpers for harnesses."""

import json
from pathlib import Path


def write_report_json(log_dir: str | Path, report_name: str, report_json: dict) -> None:
    """Write a JSON report to the harness log directory."""
    with Path(log_dir, report_name).open("w", encoding="utf-8") as file:
        file.write(json.dumps(report_json))
