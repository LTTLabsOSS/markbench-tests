"""Black Myth Wukong test script"""

import logging
import re
import sys
import time
from pathlib import Path

import vgamepad as vg

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.files import copy_to_directory, reset_directory
from harness_utils.screenshot import capture_screenshot_png
from harness_utils.input import mangohud_log_toggle, user
from harness_utils.controllers import LTTGamePad360
from harness_utils.ocr_service import find_word
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.paths import game_install_path
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
ARTIFACTS_DIRECTORY = LOG_DIRECTORY / "artifacts"
PROCESS_NAME = "b1-Win64-Shipping.exe"
STEAM_GAME_ID = 3132990
CONFIG_LOCATION = (
    game_install_path(STEAM_GAME_ID) / "b1" / "Saved" / "Config" / "Windows"
)
CONFIG_FILENAME = "GameUserSettings.ini"


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"LastUserConfirmedResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"LastUserConfirmedResolutionSizeX=(\d+)")
    cfg = CONFIG_LOCATION / CONFIG_FILENAME
    height_value: int = 0
    width_value: int = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = int(height_match.group(1))
            if width_match is not None:
                width_value = int(width_match.group(1))
    return (height_value, width_value)


def start_game():
    """Starts the game process"""
    exec_steam_game(STEAM_GAME_ID)
    logging.info("Launching Game from Steam")


def run_benchmark():
    """Starts the benchmark"""
    start_game()
    gamepad = LTTGamePad360()
    setup_start_time = int(time.time())
    reset_directory(ARTIFACTS_DIRECTORY)
    time.sleep(20)

    if find_word(word="black", timeout=30, interval=1) is None:
        logging.info("Did not find the welcome screen. Did the game launch correctly?")
        sys.exit(1)
    time.sleep(5)
    if is_linux():
        mangohud_log_toggle()
    else:
        gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    benchmark_result = find_word(word="benchmark", timeout=30, interval=1)
    if benchmark_result is None:
        logging.info("did not find main menu")
        sys.exit(1)
    if is_linux():
        user.move_mouse(benchmark_result["x"], benchmark_result["y"])
    time.sleep(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    time.sleep(0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if find_word(word="loop", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the benchmark settings menu. Did the game navigate to the settings correctly?"
        )
        sys.exit(1)
    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=3, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    if find_word(word="calibration", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the display settings menu. Did the game navigate the settings correctly?"
        )
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "display.png")

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, n=2, pause=0.5)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    # We do a little toggling here in order to get the settings to update correctly, because wukong has no true full screen option
    if find_word(word="windowed", timeout=30, interval=1) is None:
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

    if find_word(word="super", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the top of the graphics menu. Did the game navigate the settings menu correctly?"
        )
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "graphics_1.png")

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, n=9, pause=0.5)

    if find_word(word="reflection", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the bottom of the graphics menu. Did the game scroll down the graphics settings menu correctly?"
        )
        sys.exit(1)
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "graphics_2.png")

    gamepad.press_n_times(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B, n=2, pause=0.5)
    time.sleep(2)

    if find_word(word="benchmark", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the option to start the benchmark. Did the game exit the settings menu correctly?"
        )
        sys.exit(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(2)

    if find_word(word="confirm", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the confirmation to start the benchmark. Did the game select the start benchmark option correctly?"
        )
        sys.exit(1)
    gamepad.single_press(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    time.sleep(0.5)

    # log set up time
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = find_word("current", interval=1, timeout=100)
    if not result:
        logging.info("Could not find current. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time()) - 2

    time.sleep(142)

    if find_word(word="result", timeout=30, interval=1) is None:
        logging.info("Did not find result screen. Did the benchmark run?")
        sys.exit(1)

    test_end_time = int(time.time()) - 1
    time.sleep(5)
    if is_linux():
        mangohud_log_toggle()
    capture_screenshot_png(ARTIFACTS_DIRECTORY / "results.png")
    copy_to_directory(CONFIG_LOCATION / CONFIG_FILENAME, ARTIFACTS_DIRECTORY)
    time.sleep(0.5)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_process(PROCESS_NAME)


    return test_start_time, test_end_time


def main():
    """entry point"""
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIRECTORY)
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_process(PROCESS_NAME)
        sys.exit(1)
