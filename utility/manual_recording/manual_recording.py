"""Wait for the user to stop a manual recording in MarkBench."""

import sys
import time
import tkinter as tk
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output_logging import setup_logging
from harness_utils.report import seconds_to_milliseconds, write_report_json

LOG_DIRECTORY = Path(__file__).resolve().parent / "run"


def main() -> None:
    setup_logging(LOG_DIRECTORY)
    start_time = seconds_to_milliseconds(time.time())

    window = tk.Tk()
    window.title("Manual Recording")
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


if __name__ == "__main__":
    main()
