"""Black Myth Wukong test script"""

import logging
import os
import re
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import pydirectinput as user
import vgamepad as vg

sys.path.insert(1, os.path.join(sys.path[0], "../.."))

# pylint: disable=wrong-import-position
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import KerasService
from harness_utils.misc import LTTGamePad360
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_app_install_location, get_build_id

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")
PROCESS_NAME = "b1-Win64-Shipping.exe"
STEAM_GAME_ID = 3132990
CONFIG_LOCATION = (
    f"{get_app_install_location(STEAM_GAME_ID)}\\b1\\Saved\\Config\\Windows"
)
CONFIG_FILENAME = "GameUserSettings.ini"

user.FAILSAFE = False


def read_current_resolution():
    """Reads resolutions settings from local game file"""
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


def start_game():
    """Starts the game process"""
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")


def run_benchmark(keras_service):
    """Starts the benchmark"""
    start_game()
    gamepad = LTTGamePad360()
    setup_start_time = int(time.time())
    am = ArtifactManager(LOG_DIR)
    time.sleep(20)

    if keras_service.wait_for_word(word="black", timeout=30, interval=1) is None:
        logging.info("Did not find the welcome screen. Did the game launch correctly?")
        sys.exit(1)
    # We pause here to allow the option to enter the menu to appear as sometimes the word black shows up first
    time.sleep(2)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(2)

    if keras_service.wait_for_word(word="settings", timeout=30, interval=1) is None:
        logging.info("Did not find the settings option. Did the game launch correctly?")
        sys.exit(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if keras_service.wait_for_word(word="loop", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the benchmark settings menu. Did the game navigate to the settings correctly?"
        )
        sys.exit(1)
    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=3, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if keras_service.wait_for_word(word="calibration", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the display settings menu. Did the game navigate the settings correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "display.png", ArtifactType.CONFIG_IMAGE, "screenshot of display settings"
    )

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=2, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    # We do a little toggling here in order to get the settings to update correctly, because wukong has no true full screen option
    if keras_service.wait_for_word(word="windowed", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the keyword 'windowed'. Did the game select the display mode setting correctly?"
        )
        sys.exit(1)
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

    # navigate to graphics menu
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if keras_service.wait_for_word(word="super", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the top of the graphics menu. Did the game navigate the settings menu correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_1.png", ArtifactType.CONFIG_IMAGE, "first screenshot of graphics menu"
    )

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, n=9, pause=0.5)

    if keras_service.wait_for_word(word="reflection", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the bottom of the graphics menu. Did the game scroll down the graphics settings menu correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_2.png",
        ArtifactType.CONFIG_IMAGE,
        "second screenshot of graphics menu",
    )

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B, n=2, pause=0.5)
    time.sleep(2)

    if keras_service.wait_for_word(word="benchmark", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the option to start the benchmark. Did the game exit the settings menu correctly?"
        )
        sys.exit(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(2)

    if keras_service.wait_for_word(word="confirm", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the confirmation to start the benchmark. Did the game select the start benchmark option correctly?"
        )
        sys.exit(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    # log set up time
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = keras_service.wait_for_word("current", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find current. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time()) - 2

    time.sleep(142)

    if keras_service.wait_for_word(word="result", timeout=30, interval=1) is None:
        logging.info("Did not find result screen. Did the benchmark run?")
        sys.exit(1)

    test_end_time = int(time.time()) - 1
    time.sleep(5)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    am.copy_file(
        f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}",
        ArtifactType.CONFIG_TEXT,
        "GameUserSettings.ini",
    )
    time.sleep(0.5)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time


def setup_logging():
    """setup logging"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(
        filename=f"{LOG_DIR}/harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def main():
    """entry point"""
    parser = ArgumentParser()
    parser.add_argument(
        "--kerasHost",
        dest="keras_host",
        help="Host for Keras OCR service",
        required=True,
    )
    parser.add_argument(
        "--kerasPort",
        dest="keras_port",
        help="Port for Keras OCR service",
        required=True,
    )
    args = parser.parse_args()
    keras_service = KerasService()
    start_time, endtime = run_benchmark(keras_service)
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
