"""Cities: Skylines II test script"""

import logging
import os
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from citiesskylines2_utils import (
    copy_benchmarksave,
    copy_continuegame,
    copy_launcherfiles,
    copy_launcherpath,
    read_current_resolution,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.keras_service import (
    KerasService,
    ScreenShotDivideMethod,
    ScreenShotQuadrant,
    ScreenSplitConfig,
)
from harness_utils.misc import mouse_scroll_n_times
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "cities2.exe"
STEAM_GAME_ID = 949230
top_left_keras = ScreenSplitConfig(
    divide_method=ScreenShotDivideMethod.QUADRANT, quadrant=ScreenShotQuadrant.TOP_LEFT
)
bottom_left_keras = ScreenSplitConfig(
    divide_method=ScreenShotDivideMethod.QUADRANT, quadrant=ScreenShotQuadrant.BOTTOM_LEFT
)

launcher_files = ["bootstrapper-v2.exe", "launcher.exe", "notlauncher-options.json"]
save_files = ["Benchmark.cok", "Benchmark.cok.cid"]
config_files = ["UserState.coc"]

APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = Path(f"{APPDATA}\\..\\LocalLow\\Colossal Order\\Cities Skylines II")
CONFIG_FILENAME = "launcher-settings.json"
CONFIG_FULL_PATH = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"

user.FAILSAFE = False


def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(STEAM_GAME_ID)


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")

def time_check(keras_service, timeout=300, interval=0.5):
    """Continuously looks for the time of 08:18 using kerasService. If not found in the given time, marks the out time."""
    start = time.monotonic()
    next_tick = start

    while time.monotonic() - start < timeout:
        now = time.monotonic()

        # enforce fixed cadence
        if now < next_tick:
            time.sleep(next_tick - now)
            continue

        next_tick += interval

        found = keras_service.look_for_word(
            word="18",
            attempts=1,
            interval=0.2,
            split_config=bottom_left_keras
        )

        if found:
            user.press("space")
            return True

    return False


def run_benchmark(keras_service):
    """Starts the benchmark"""
    copy_launcherfiles(launcher_files)
    copy_launcherpath()
    copy_benchmarksave(save_files)
    copy_continuegame(config_files)

    am = ArtifactManager(LOG_DIRECTORY)

    start_game()
    setup_start_time = int(time.time())
    time.sleep(14)

    result = keras_service.wait_for_word("paradox", interval=0.5, timeout=100)
    if not result:
        logging.info("Could not find the Paradox logo. Did the game launch?")
        sys.exit(1)
    user.press("esc")
    user.press("esc")
    user.press("esc")
    time.sleep(15)

    result = keras_service.wait_for_word("new", interval=0.5, timeout=100)
    if not result:
        logging.info("Did not find the main menu. Did the game crash?")
        sys.exit(1)

    result = keras_service.look_for_word("load", attempts=10, interval=1)
    if not result:
        logging.info("Did not find the load game option. Did the save game copy?")
        sys.exit(1)

    # Navigate to load save menu
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)

    result = keras_service.look_for_word(
        "benchmark", attempts=10, interval=1, split_config=top_left_keras
    )
    if not result:
        logging.info(
            "Did not find the save game original date. Did the keras click correctly?"
        )
        sys.exit(1)

    # Loading the game
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)
    user.press("enter")
    time.sleep(10)

    result = keras_service.wait_for_word("grand", interval=0.5, timeout=100)
    if not result:
        logging.info(
            "Could not find the paused notification. Unable to mark start time!"
        )
        sys.exit(1)
    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    gui.moveTo(result["x"], result["y"])
    time.sleep(2)
    logging.info("Starting benchmark")
    user.press("3")

    #mark in of benchmark start
    benchmark_start_time = int(time.time())
    time.sleep(3)

    #supposed to be window start time
    test_start_time = int(time.time())
    time.sleep(80)
    if not time_check(keras_service):
        logging.info("Timeout reached...")
        sys.exit(1)

    result = keras_service.wait_for_word("paused", interval=0.5, timeout=100)
    if not result:
        logging.info(
            "Could not find the paused notification. Unable to mark start time!"
        )
        sys.exit(1)

    test_end_time = int(time.time())

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    # End the run
    elapsed_test_time = round(test_end_time - benchmark_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Open quick menu
    user.press("esc")
    time.sleep(0.2)

    result = keras_service.look_for_word("options", attempts=10, interval=1)
    if not result:
        logging.info(
            "Did not find the options menu. Did the game open the quick dialog menu properly?"
        )
        sys.exit(1)

    # Navigate to options menu
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)

    am.take_screenshot(
        "general.png", ArtifactType.CONFIG_IMAGE, "general settings menu"
    )

    result = keras_service.look_for_word("graphics", attempts=10, interval=1)
    if not result:
        logging.info(
            "Did not find the graphics menu. Did the game navigate to the general settings correctly?"
        )
        sys.exit(1)

    # Navigate to graphics menu
    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)
    gui.click()
    time.sleep(0.2)

    am.take_screenshot(
        "graphics_1.png",
        ArtifactType.CONFIG_IMAGE,
        "first picture of graphics settings menu",
    )

    result = keras_service.look_for_word("window", attempts=10, interval=1)
    if not result:
        logging.info(
            "Did not find the keyword 'window' in graphics menu. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)

    gui.moveTo(result["x"], result["y"])
    time.sleep(0.2)

    mouse_scroll_n_times(8, -400, 0.2)

    if keras_service.wait_for_word(word="water", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the keyword 'water' in menu. Did the game scroll correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_2.png",
        ArtifactType.CONFIG_IMAGE,
        "second picture of graphics settings menu",
    )

    mouse_scroll_n_times(8, -400, 0.2)

    # verify that we scrolled through the menu correctly
    if keras_service.wait_for_word(word="texture", timeout=30, interval=1) is None:
        logging.info(
            "Did not find the keyword 'texture' in menu. Did the game scroll correctly?"
        )
        sys.exit(1)
    am.take_screenshot(
        "graphics_3.png",
        ArtifactType.CONFIG_IMAGE,
        "third picture of graphics settings menu",
    )
    am.copy_file(CONFIG_FULL_PATH, ArtifactType.CONFIG_TEXT, "config file")

    # Exit
    terminate_processes(PROCESS_NAME)
    am.create_manifest()

    return test_start_time, test_end_time, elapsed_test_time


def main():
    """main entry point to the script"""
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
    keras_service = KerasService(args.keras_host, args.keras_port)

    test_start_time, test_end_time, elapsed_test_time = run_benchmark(keras_service)
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(test_start_time),
        "end_time": seconds_to_milliseconds(test_end_time),
        "benchmark_time": (elapsed_test_time),
        "benchmark_time_unit": "seconds",
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
        terminate_processes(PROCESS_NAME)
        sys.exit(1)
