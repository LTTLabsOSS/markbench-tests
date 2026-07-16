"""Hitman World of Assassination test script"""

import logging
import os
import sys
import time
import winreg
from pathlib import Path

import psutil
import pyautogui as gui
from hitman3_utils import (
    get_benchmark_name,
    get_resolution,
    process_registry_file,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import capture_and_save_screenshot, copy_artifact
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.steam import exec_steam_run_command, get_build_id

STEAM_GAME_ID = 1659040
STEAM_PATH = Path(os.environ["ProgramFiles(x86)"]) / "steam"
STEAM_EXECUTABLE = "steam.exe"
PROCESS_NAMES = ["HITMAN3.exe", "Launcher.exe"]
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
INPUT_FILE = SCRIPT_DIRECTORY / "graphics.reg"
CONFIG_FILE = SCRIPT_DIRECTORY / "graphics_config.txt"
hive = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\\IO Interactive\\HITMAN3"


def benchmark_check():
    """Return the benchmark name and expected runtime for the selected scene."""
    benchmark_id = get_benchmark_name(str(CONFIG_FILE))
    if benchmark_id == 0:
        selected_benchmark_name = "Hitman World of Assassination: Dubai"
        benchmark_time = 102
    elif benchmark_id == 1:
        selected_benchmark_name = "Hitman World of Assassination: Dartmoor"
        benchmark_time = 140
    else:
        raise ValueError(
            "Could not determine the benchmark. Is there an error in the registry?"
        )

    return selected_benchmark_name, benchmark_time


def run_benchmark():
    """Run the benchmark flow, capture artifacts, and return timing data."""
    setup_start_time = int(time.time())
    process_registry_file(hive, SUBKEY, str(INPUT_FILE), str(CONFIG_FILE))
    copy_artifact(CONFIG_FILE, ARTIFACTS_DIRECTORY)
    selected_benchmark_name, benchmark_time = benchmark_check()
    exec_steam_run_command(STEAM_GAME_ID)

    time.sleep(2)
    location = gui.locateOnScreen(
        f"{SCRIPT_DIRECTORY}\\screenshots\\options.png", confidence=0.7
    )  # luckily this seems to be a set resolution for the button
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Options1.png")
    time.sleep(1)
    gui.scroll(-1000)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "Options2.png")
    time.sleep(2)

    location = gui.locateOnScreen(
        f"{SCRIPT_DIRECTORY}\\screenshots\\start_benchmark.png", confidence=0.7
    )  # luckily this seems to be a set resolution for the button
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    time.sleep(5)

    result = find_word("crowd", timeout=20, interval=1)
    if not result:
        logging.info(
            "Did not find the statistics in the corner. Did the benchmark launch?"
        )
        raise RuntimeError("Benchmark failed.")

    benchmark_start_time = int(time.time())

    time.sleep(
        benchmark_time
    )  # sleep during the benchmark which is indicated based on the benchmark detected.

    result = find_word("overall", timeout=20, interval=1)
    if not result:
        logging.info("Did not find the overall FPS score. Did the benchmark crash?")
        raise RuntimeError("Benchmark failed.")

    benchmark_end_time = int(time.time()) - 1
    elapsed_test_time = round(benchmark_end_time - benchmark_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    time.sleep(1)

    for process in psutil.process_iter():
        try:
            if process.name() in PROCESS_NAMES:
                process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignore processes that no longer exist or cannot be accessed


    return benchmark_start_time, benchmark_end_time, selected_benchmark_name


setup_logging(LOG_DIRECTORY)

try:
    test_start_time, test_end_time, benchmark_name = run_benchmark()
    height, width = get_resolution(str(CONFIG_FILE))
    report = {
        "resolution": f"{width}x{height}",
        "benchmark": benchmark_name,
        "start_time": seconds_to_milliseconds(
            test_start_time
        ),  # seconds * 1000 = millis
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        try:
            if proc.name() in PROCESS_NAMES:
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignore processes that no longer exist or cannot be accessed

    sys.exit(1)
