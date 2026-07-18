"""Rainbow Six Siege test script"""

import logging
from pathlib import Path
import time
import sys
import vgamepad as vg
from r6siege_utils import read_current_resolution, get_r6s_config_path, find_latest_result_file

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.process import terminate_process
from harness_utils.input import user
from harness_utils.output_logging import setup_logging
from harness_utils.ocr_service import find_word
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.controllers import LTTGamePadDS4

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "rainbowsix.exe"
STEAM_GAME_ID = 359550
GAMEPAD = LTTGamePadDS4()

user.FAILSAFE = False

def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID)

def run_benchmark(am):
    """Starts the benchmark"""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(90)

    #Checking for the main menu
    if find_word(word="conflict", interval=1, timeout=15):
        user.press("down")
        time.sleep(0.4)
        user.press("enter")
        time.sleep(30)

    #Checking for the main menu
    if find_word(word="shop", interval=1, timeout=60) is None:
        logging.info("Did not find the main menu. Did the game load?")
        sys.exit(1)

    #Navigating to the options
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS)

    if find_word(word="options", interval=0.5, timeout=100) is None:
        logging.info("Could not find the options menu. Was something else on the screen?")
        sys.exit(1)

    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    #Navigating to the display settings and screenshotting
    if find_word(word="general", interval=0.5, timeout=100) is None:
        logging.info("Could not find the general options. Did it navigate to the settings correctly?")
        sys.exit(1)

    GAMEPAD.button_press_n_times(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT, n=3, pause=0.3)

    if find_word(word="monitor", interval=0.5, timeout=100) is None:
        logging.info("Could not find the monitor. Did it navigate to the display settings correctly?")
        sys.exit(1)

    time.sleep(1)
    am.take_screenshot("display1.png", ArtifactType.CONFIG_IMAGE, "First screenshot of the display settings")
    time.sleep(1)
    GAMEPAD.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=12, pause=0.3)
    am.take_screenshot("display2.png", ArtifactType.CONFIG_IMAGE, "Second screenshot of the display settings")
    time.sleep(1)

    #Navigating to the graphics settings and screenshotting
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT)

    if find_word(word="filtering", interval=0.5, timeout=100) is None:
        logging.info("Could not find the texture filtering setting. Did it navigate to the graphics settings correctly?")
        sys.exit(1)

    time.sleep(1)
    am.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "1st screenshot of the graphics settings")
    time.sleep(1)

    GAMEPAD.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=17, pause=0.3)

    if find_word(word="fps", interval=0.5, timeout=100) is None:
        logging.info("Could not find the TAA sharpness setting. Did it navigate the graphics settings correctly?")
        sys.exit(1)

    time.sleep(1)
    am.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "2nd screenshot of the graphics settings")
    time.sleep(1)

    GAMEPAD.dpad_press_n_times(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH, n=3, pause=0.3)

    if find_word(word="sharpness", interval=0.5, timeout=100) is None:
        logging.info("Could not find the TAA sharpness setting. Did it navigate the graphics settings correctly?")
        sys.exit(1)

    time.sleep(1)
    am.take_screenshot("graphics3.png", ArtifactType.CONFIG_IMAGE, "3rd screenshot of the graphics settings")
    time.sleep(1)

    #Starting the benchmark
    GAMEPAD.single_button_press(button=vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT)

    elapsed_setup_time = int(time.time() - setup_start_time)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    if find_word(word="skip", interval=0.5, timeout=100) is None:
        logging.info("Could not find the skip dialog. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())
    time.sleep(76)

    if find_word(word="results", interval=0.2, timeout=250) is None:
        logging.info("Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    test_end_time = int(time.time() - 1)
    time.sleep(1)
    am.take_screenshot("results.png", ArtifactType.CONFIG_IMAGE, "Screenshot of the results")
    am.copy_file(find_latest_result_file(), ArtifactType.RESULTS_TEXT, "Benchmark results HTML")

    # Wait 5 seconds for benchmark info
    time.sleep(2)

    # End the run
    elapsed_test_time = int(test_end_time - test_start_time)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    am.copy_file(get_r6s_config_path(), ArtifactType.CONFIG_TEXT, "GameSettings.ini")
    terminate_process(PROCESS_NAME)
    width, height = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    logging.info("Waiting for Siege X to fully exit now.")
    time.sleep(30) #sleeping to let the game processes finish closing

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)


def main():
    """entry point"""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    run_benchmark(am)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_process(PROCESS_NAME)
        sys.exit(1)