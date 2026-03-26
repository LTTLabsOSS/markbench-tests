"""Black Myth Wukong test script."""

import logging
import re
import sys
import time
from pathlib import Path

import vgamepad as vg

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word
from harness_utils.misc import LTTGamePad360
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_app_install_location, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "b1-Win64-Shipping.exe"
STEAM_GAME_ID = 3132990
CONFIG_LOCATION = (
    f"{get_app_install_location(STEAM_GAME_ID)}\\b1\\Saved\\Config\\Windows"
)
CONFIG_FILENAME = "GameUserSettings.ini"


def read_current_resolution():
    """Read resolutions settings from local game file."""
    height_pattern = re.compile(r"LastUserConfirmedResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"LastUserConfirmedResolutionSizeX=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def launch_game() -> None:
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    gamepad = LTTGamePad360()
    setup_start_time = int(time.time())
    time.sleep(20)

    if not find_word("black", timeout=30, interval=1, msg="Did not find the welcome screen. Did the game launch correctly?"):
        return FAILED_RUN
    time.sleep(2)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(2)

    if not find_word("settings", timeout=30, interval=1, msg="Did not find the settings option. Did the game launch correctly?"):
        return FAILED_RUN
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if not find_word("loop", timeout=30, interval=1, msg="Did not find the benchmark settings menu. Did the game navigate to the settings correctly?"):
        return FAILED_RUN
    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=3, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if not find_word("calibration", timeout=30, interval=1, msg="Did not find the display settings menu. Did the game navigate the settings correctly?"):
        return FAILED_RUN
    am.take_screenshot("01_display.png", ArtifactType.CONFIG_IMAGE)

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=2, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if not find_word("windowed", timeout=30, interval=1, msg="Did not find the keyword 'windowed'. Did the game select the display mode setting correctly?"):
        return FAILED_RUN
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
    time.sleep(0.5)
    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A, n=3, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if not find_word("super", timeout=30, interval=1, msg="Did not find the top of the graphics menu. Did the game navigate the settings menu correctly?"):
        return FAILED_RUN
    am.take_screenshot("02_graphics_1.png", ArtifactType.CONFIG_IMAGE)

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, n=9, pause=0.5)
    if not find_word("reflection", timeout=30, interval=1, msg="Did not find the bottom of the graphics menu. Did the game scroll down the graphics settings menu correctly?"):
        return FAILED_RUN
    am.take_screenshot("03_graphics_2.png", ArtifactType.CONFIG_IMAGE)

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B, n=2, pause=0.5)
    time.sleep(2)

    if not find_word("benchmark", timeout=30, interval=1, msg="Did not find the option to start the benchmark. Did the game exit the settings menu correctly?"):
        return FAILED_RUN
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(2)

    if not find_word("confirm", timeout=30, interval=1, msg="Did not find the confirmation to start the benchmark. Did the game select the start benchmark option correctly?"):
        return FAILED_RUN
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("current", interval=0.5, timeout=100, msg="Could not find current. Unable to mark start time!"):
        return FAILED_RUN

    test_start_time = int(time.time()) - 2
    time.sleep(142)

    if not find_word("result", timeout=30, interval=1, msg="Did not find result screen. Did the benchmark run?"):
        return FAILED_RUN

    test_end_time = int(time.time()) - 1
    time.sleep(5)
    am.take_screenshot("04_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}", ArtifactType.CONFIG_TEXT, "GameUserSettings.ini")
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the Black Myth Wukong benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = read_current_resolution()
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
            }
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
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
