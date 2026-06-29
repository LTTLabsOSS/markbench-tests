"""Dawntrail test script"""

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
RESULTS_DIRECTORY = Path("C:/Users/Labs/Downloads/ffxiv-dawntrail-bench_v11/ffxivbenchmarklauncher.ini")

user.FAILSAFE = False

# Possible ini locations, its like this cause I was getting pathing issues
POSSIBLE_INI_PATHS = [
    Path(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\ffxivbenchmarklauncher.ini"),
    Path(r"C:\Users\Labs\Documents\My Games\FINAL FANTASY XIV - DAWNTRAIL\ffxivbenchmarklauncher.ini"),
    Path.home() / "Documents" / "My Games" / "FINAL FANTASY XIV - DAWNTRAIL" / "ffxivbenchmarklauncher.ini",
    Path(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\output.ini")# sometimes different name
]
def read_output_stats(index: int, retries=8, delay=3):
    config = configparser.ConfigParser()
    logging.info("Looking for benchmark results ini file...")
    for attempt in range(retries):
        for ini_path in POSSIBLE_INI_PATHS:
            if ini_path.exists():
                logging.info(f"✅ Found results file: {ini_path}")
                try:
                    config.read(str(ini_path))
                    if 'SCORE' in config:
                        logging.info("✅ [SCORE] section found!")
                        if index == 0:
                            return config.getint('SCORE', 'SCORE')
                        else:
                            width = config.get('SCORE', 'SCORE_SCREENWIDTH')
                            height = config.get('SCORE', 'SCORE_SCREENHEIGHT')
                            return f"{width} x {height}"
                    else:
                        logging.warning(f"[SCORE] section missing in {ini_path}")
                except Exception as e:
                    logging.warning(f"Error reading {ini_path}: {e}")
        logging.info(f"Attempt {attempt+1}/{retries} - waiting for results...")
        time.sleep(delay)
    # Final debug info
    logging.error("❌ Could not find valid results after all attempts.")
    logging.error("Searched in these locations:")
    for p in POSSIBLE_INI_PATHS:
        logging.error(f"  - {p} (exists: {p.exists()})")
    raise RuntimeError("Could not read SCORE section from results ini"
    
def start_game():
    logging.info("Starting Program...")
    #Minimize MarkBench
    # Find all windows that match the process title
    windows = gw.getWindowsWithTitle("Markbench")
    # Minimize the first window found
    if windows:
        logging.info(windows)
        windows[0].minimize()
    """Launch the benchmark"""
    return os.startfile(r"C:\Users\Labs\Downloads\ffxiv-dawntrail-bench_v11\ffxiv-dawntrail-bench.exe")

def navigate_to_settings():
    logging.info(RESULTS_DIRECTORY)
    logging.info("Navigating launcher")
    """navigate from main launcher menu to settings menu"""
    result = find_word("settings", timeout=10)
    user.click(int(result['x']), int(result['y']))

def navigate_settings() -> None:
    """Simulate inputs to navigate the main menu"""
    navigate_to_settings()
    user.press("tab")
    time.sleep(0.5)
    am.take_screenshot(
        "graphics.png", ArtifactType.CONFIG_IMAGE, "graphics settings menu"
    )
    user.press("right")
    user.press("right")
    user.press("right")
    user.press("right")
    am.take_screenshot(
        "display.png", ArtifactType.CONFIG_IMAGE, "display settings menu"
    )
    user.press("right")
    user.press("right")
    user.press("right")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("tab")
    user.press("enter")

def run_benchmark():
    """Start the benchmark"""
    # Start game via Steam and enter fullscreen mode
    setup_start_time = int(time.time())
    start_game()
    time.sleep(5)
    navigate_settings()
    # Start the benchmark!
    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    user.press("tab")
    user.press("down")
    user.press("down")
    result = find_word("start", timeout=10)
    startpos = (result['x'],result['y'])
    user.press("up")
    user.press("up")
    user.click(startpos[0], startpos[1])
    test_start_time = int(time.time()) - 5
    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(180)
    result = find_word("total", timeout=300, interval=0.5)
    if not result:
        logging.info("Did not see results screen. Mark as DNF.") 
        sys.exit(1)
    time.sleep(5)
    am.take_screenshot(
        "results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark"
    )
    test_end_time = int(time.time()) - 2
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    terminate_process(PROCESS_NAME)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    resolution = read_output_stats(1)
    score = read_output_stats(0)
    report = {
        "score": f"{score}",
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
