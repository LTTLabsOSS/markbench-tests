"""Wait for the user to stop a MarkBench recording session."""

import logging
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output_logging import setup_logging
from harness_utils.report import seconds_to_milliseconds, write_report_json

logger = logging.getLogger(__name__)
LOG_DIRECTORY = Path(__file__).resolve().parent / "run"


def main() -> int:
    setup_logging(LOG_DIRECTORY)
    start_time = seconds_to_milliseconds(time.time())

    try:
        import tkinter as tk
    except ImportError:
        logger.exception("Python needs Tk support to open the recording window.")
        return 1

    try:
        window = tk.Tk()
    except tk.TclError:
        logger.exception("Cannot open the recording window. Check Tk and the display.")
        return 1

    window.title("Recording Session")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    stop_button = tk.Button(window, text="Stop", width=16, command=window.destroy)
    stop_button.pack(padx=16, pady=16)
    window.mainloop()

    report = {
        "start_time": start_time,
        "end_time": seconds_to_milliseconds(time.time()),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
