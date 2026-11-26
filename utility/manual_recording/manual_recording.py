"""Wait for MarkBench to stop a manual recording."""

import json
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
RUN_DIR = HARNESS_DIR / "run"
STOP_FILE = RUN_DIR / "stop"


def claim_stop_file() -> None:
    while True:
        try:
            STOP_FILE.unlink()
            return
        except FileNotFoundError:
            time.sleep(0.2)


def main() -> None:
    start_time = round(time.time() * 1000)
    claim_stop_file()
    report = {"start_time": start_time, "end_time": round(time.time() * 1000)}
    (RUN_DIR / "report.json").write_text(json.dumps(report), encoding="utf-8")


if __name__ == "__main__":
    main()
