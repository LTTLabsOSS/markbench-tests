"""Far Cry 6 test script."""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import pyautogui as gui

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from farcry6_utils import get_resolution
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import mouse_scroll_n_times
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "FarCry6.exe"
GAME_ID = 5266
username = os.getlogin()
XML_FILE = rf"C:\Users\{username}\Documents\My Games\Far Cry 6\gamerprofile.xml"


def launch_game() -> None:
    subprocess.run(f"start uplay://launch/{GAME_ID}/0", shell=True, check=True)


def click_result(result: dict) -> None:
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(25)

    if not find_word("warning", timeout=20, interval=1, msg="Did not see warnings. Did the game start?"):
        return FAILED_RUN
    press("escape*8", pause=1)

    if not find_word("original", timeout=20, interval=1, msg="Did not see the Far Cry 6 intro video. Did the game crash?"):
        return FAILED_RUN
    press("space, space")
    time.sleep(2)

    if find_word("later", timeout=5, interval=1):
        press("escape")

    result = find_word("options", timeout=10, interval=1, msg="Did not find the main menu. Did the game skip the intros?")
    if not result:
        return FAILED_RUN
    click_result(result)
    time.sleep(2)

    result = find_word("video", timeout=10, interval=1, msg="Did not find the options menu. Did OCR click incorrectly?")
    if not result:
        return FAILED_RUN
    click_result(result)
    time.sleep(2)

    if not find_word("adapter", timeout=10, interval=1, msg="Did not find the Video Adapter setting in the monitor options."):
        return FAILED_RUN
    am.take_screenshot("01_video.png", ArtifactType.CONFIG_IMAGE)
    time.sleep(2)

    press("e")
    if not find_word("filtering", timeout=10, interval=1, msg="Did not find the Texture Filtering setting in the quality options."):
        return FAILED_RUN
    am.take_screenshot("02_quality_1.png", ArtifactType.CONFIG_IMAGE)
    time.sleep(2)
    mouse_scroll_n_times(8, -800, 0.2)

    if not find_word("shading", timeout=10, interval=1, msg="Did not find the FidelityFX Variable Shading setting in the quality options."):
        return FAILED_RUN
    am.take_screenshot("03_quality_2.png", ArtifactType.CONFIG_IMAGE)
    time.sleep(2)

    press("e*2")
    if not find_word("lock", timeout=10, interval=1, msg="Did not find the Enable Framerate Lock setting in the advanced options."):
        return FAILED_RUN
    am.take_screenshot("04_advanced.png", ArtifactType.CONFIG_IMAGE)

    time.sleep(2)
    press("f5")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("toggle", timeout=10, interval=1, msg="Did not find the toggle ui button in the lower right. Did the benchmark crash?"):
        return FAILED_RUN
    test_start_time = int(time.time())
    time.sleep(60)

    if not find_word("results", interval=0.5, timeout=100, msg="Didn't find the results screen. Did the benchmark crash?"):
        return FAILED_RUN
    test_end_time = int(time.time()) - 1
    am.take_screenshot("05_results.png", ArtifactType.RESULTS_IMAGE)
    time.sleep(1)
    am.copy_file(XML_FILE, ArtifactType.CONFIG_TEXT, "config file")
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0
    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            width, height = get_resolution()
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": "unknown",
            }
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        exit_code = 1
    finally:
        terminate_processes(PROCESS_NAME)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)
    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
