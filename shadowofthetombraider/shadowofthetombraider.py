"""Shadow of the Tomb Raider test script"""
import logging
import os
from pathlib import Path
import time
import pydirectinput as user
import sys
from shadow_of_the_tomb_raider_utils import get_latest_file_report, get_resolution, get_args

sys.path.insert(1, os.path.join(sys.path[0], '..'))

#pylint: disable=wrong-import-position
from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    format_resolution,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.keras_service import KerasService, ScreenShotDivideMethod, ScreenShotQuadrant, ScreenSplitConfig
from harness_utils.steam import exec_steam_game
from harness_utils.artifacts import ArtifactManager, ArtifactType

STEAM_GAME_ID = 750920
PROCESS_NAME = "SOTTR.exe"
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")


def setup_logging():
    """default logging config"""
    setup_log_directory(LOG_DIR)
    logging.basicConfig(filename=f'{LOG_DIR}/harness.log',
                        format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_DATE_FORMAT,
                        level=logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-nolauncher"])


def run_benchmark():
    """Start game via Steam and enter fullscreen mode"""
    args = get_args()
    keras_service = KerasService(args.keras_host, args.keras_port)
    am = ArtifactManager(LOG_DIR)

    setup_start_time = time.time()
    start_game()
    time.sleep(10)

    ss_config = ScreenSplitConfig(
        divide_method=ScreenShotDivideMethod.HORIZONTAL,
        quadrant=ScreenShotQuadrant.TOP
    )

    if keras_service.wait_for_word(word="options", timeout=30, interval=1, split_config=ss_config) is None:
        logging.info("Did not find the options menu. Did the game launch correctly?")
        sys.exit(1)

    logging.info("found options")

    user.press("up")
    time.sleep(0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("up")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1)

    if keras_service.wait_for_word(word="graphics", timeout=30, interval=1) is None:
        logging.info("Did not find the graphics menu. Did the menu get stuck?")
        sys.exit(1)

    logging.info("found graphics")

    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("down")
    time.sleep(0.5)
    user.press("enter")
    time.sleep(1)

    if keras_service.wait_for_word(word="benchmark", timeout=30, interval=1) is None:
        logging.info("Did not find the benchmark option on the screen. Did the menu get stuck?")
        sys.exit(1)

    am.take_screenshot("display.png", ArtifactType.CONFIG_IMAGE, "picture of display settings")

    # press up until we have DISPLAY hilighted so we can flip to the graphics tab
    for _ in range(21):
        user.press("up")
        time.sleep(0.2)

    user.press("right")
    am.take_screenshot("graphics.png", ArtifactType.CONFIG_IMAGE, "picture of graphics settings")

    user.press("r")
    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    time.sleep(2)
    test_start_time = time.time()

    # Wait for benchmark to complete
    time.sleep(180)

    test_end_time = time.time()

    result = keras_service.wait_for_word(word="tomb", timeout=10, interval=0.1)
    if result is None:
        logging.error("Unable to find the loading screen. Using default end time value.")
    else:
        test_end_time = time.time()

    if keras_service.wait_for_word(word="results", timeout=20, interval=1) is None:
        logging.error("Results screen after running benchmark not found, exiting.")
        sys.exit(1)

    logging.info("Run completed. Closing game.")

    time.sleep(2)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")

    username = os.getlogin()
    game_document_dir = Path(f"C:\\Users\\{username}\\Documents\\Shadow of the Tomb Raider")
    game_log = game_document_dir.joinpath("Shadow of the Tomb Raider.log")
    am.copy_file(Path(game_log), ArtifactType.RESULTS_TEXT, "game log")
    am.copy_file(get_latest_file_report(game_document_dir), ArtifactType.RESULTS_TEXT, "benchmark result")

    terminate_processes(PROCESS_NAME)
    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time)
    }

    am.create_manifest()
    write_report_json(LOG_DIR, "report.json", report)


if __name__ == "__main__":
    try:
        setup_logging()
        run_benchmark()
    except Exception as ex:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(ex)
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
