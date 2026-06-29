import logging
import sys
import time
import os
import configparser
import pygetwindow as gw
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.input import user
from harness_utils.ocr_service import find_word
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_process

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "ffxiv-dawntrail-bench.exe"

# Possible ini locations
POSSIBLE_INI_PATHS = [
    Path(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\ffxivbenchmarklauncher.ini"),
    Path(r"C:\Users\Labs\Documents\My Games\FINAL FANTASY XIV - DAWNTRAIL\ffxivbenchmarklauncher.ini"),
    Path.home() / "Documents" / "My Games" / "FINAL FANTASY XIV - DAWNTRAIL" / "ffxivbenchmarklauncher.ini",
    Path(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\output.ini"),
]


def read_output_stats(index: int, retries: int = 8, delay: int = 3):
    """Read benchmark results from the ini file."""
    config = configparser.ConfigParser()
    logging.info("Looking for benchmark results ini file...")

    for attempt in range(retries):
        for ini_path in POSSIBLE_INI_PATHS:
            if ini_path.exists():
                logging.info("Found results file: %s", ini_path)
                try:
                    config.read(str(ini_path))
                    if "SCORE" in config:
                        logging.info("[SCORE] section found!")
                        if index == 0:
                            return config.getint("SCORE", "SCORE")
                        else:
                            width = config.get("SCORE", "SCORE_SCREENWIDTH")
                            height = config.get("SCORE", "SCORE_SCREENHEIGHT")
                            return f"{width} x {height}"
                    else:
                        logging.warning("[SCORE] section missing in %s", ini_path)
                except Exception as e:  # pylint: disable=broad-except
                    logging.warning("Error reading %s: %s", ini_path, e)

        logging.info("Attempt %d/%d - waiting for results...", attempt + 1, retries)
        time.sleep(delay)

    # Final debug info
    logging.error("Could not find valid results after all attempts.")
    for p in POSSIBLE_INI_PATHS:
        logging.error("  - %s (exists: %s)", p, p.exists())
    raise RuntimeError("Could not read SCORE section from results ini")


def start_game():
    """Launch the benchmark executable."""
    logging.info("Starting Program...")

    # Minimize MarkBench window if present
    windows = gw.getWindowsWithTitle("Markbench")
    if windows:
        windows[0].minimize()

    os.startfile(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\ffxiv-dawntrail-bench.exe")


def navigate_to_settings():
    """Navigate from main launcher menu to settings."""
    result = find_word("settings", timeout=10)
    user.click(int(result["x"]), int(result["y"]))


def navigate_settings() -> None:
    """Navigate through settings tabs."""
    navigate_to_settings()

    user.press("tab")
    time.sleep(0.5)

    am.take_screenshot("graphics.png", ArtifactType.CONFIG_IMAGE, "graphics settings menu")

    for _ in range(4):
        user.press("right")

    am.take_screenshot("display.png", ArtifactType.CONFIG_IMAGE, "display settings menu")

    for _ in range(3):
        user.press("right")

    for _ in range(9):
        user.press("tab")

    user.press("enter")


def run_benchmark():
    """Run the full benchmark sequence."""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(5)

    navigate_settings()

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %.2f seconds", elapsed_setup_time)

    # Start benchmark
    user.press("tab")
    user.press("down")
    user.press("down")

    result = find_word("start", timeout=10)
    start_pos = (result["x"], result["y"])

    user.press("up")
    user.press("up")
    user.click(start_pos[0], start_pos[1])

    test_start_time = int(time.time()) - 5
    logging.info("Benchmark started. Waiting for completion...")

    time.sleep(180)

    result = find_word("total", timeout=300, interval=0.5)
    if not result:
        logging.error("Did not see results screen. Marking as DNF.")
        sys.exit(1)

    time.sleep(5)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark")

    test_end_time = int(time.time()) - 2
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %.2f seconds", elapsed_test_time)

    time.sleep(3)
    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


# ====================== Main ======================
setup_logging(LOG_DIRECTORY)
am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    resolution = read_output_stats(1)
    score = read_output_stats(0)

    report = {
        "score": str(score),
        "resolution": str(resolution),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)

except Exception as e:  # pylint: disable=broad-except
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
