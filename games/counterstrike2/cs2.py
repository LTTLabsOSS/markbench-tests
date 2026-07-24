"""Counter-Strike 2 test script"""

import logging
import sys
import time
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from cs2_utils import get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import (
    exec_steam_game,
    get_build_id,
    get_active_steam_account_id,
    get_steam_folder_path,
)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "cs2.exe"
STEAM_GAME_ID = 730

STEAM_USER_ID = get_active_steam_account_id()
CFG = Path(
    get_steam_folder_path(),
    "userdata",
    str(STEAM_USER_ID),
    str(STEAM_GAME_ID),
    "local",
    "cfg",
    "cs2_video.txt",
)

user.FAILSAFE = False


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["-console", "+fps_max 0"])


def wait_for_word(word, timeout=30, interval=1, why: str = ""):
    """Function for wait for word"""
    result = find_word(word, timeout=timeout, interval=interval)
    if not result:
        raise RuntimeError(f"Did not find {word} to {why}")
    return result


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def identify_settings():
    """Checks the resolution to click the settings cog"""
    height, width = get_resolution()
    location = None

    match width:
        case "1920":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1080.png",
                minSearchTime=5,
                confidence=0.6,
            )
        case "2560":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1440.png",
                minSearchTime=5,
                confidence=0.6,
            )
        case "3840":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_2160.png",
                minSearchTime=5,
                confidence=0.6,
            )
        case _:
            logging.error(
                "Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?",
                height,
                width,
            )
            raise RuntimeError

    if location is None:
        logging.error(
            "Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?",
            height,
            width,
        )
        raise RuntimeError

    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)


def navigate_settings():
    """Navigates the settings menu and takes screenshots for traceability"""

    result = wait_for_word(
        word="video", timeout=10, interval=1, why="find the video menu button"
    )

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    wait_for_word(word="brightness", why="find the video settings")

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "video.png")

    result = wait_for_word(
        word="advanced", timeout=10, interval=1, why="find the advanced video menu"
    )

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced_video_1.png")

    result = wait_for_word(
        word="boost",
        timeout=10,
        interval=1,
        why="identify we're in the advanced video menu",
    )

    gui.moveTo(result["x"], result["y"])
    time.sleep(1)
    gui.scroll(-6000000)
    time.sleep(1)

    wait_for_word(word="particle", why="verify we scrolled correctly")

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "advanced_video_2.png")


def execute_benchmark():
    """Starts the benchmark"""
    logging.info("Starting benchmark")

    result = wait_for_word(
        word="play", timeout=10, interval=1, why="click the play tab"
    )

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = wait_for_word(
        word="workshop", timeout=10, interval=1, why="click the workshop tab"
    )

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = wait_for_word(
        word="fps", timeout=10, interval=1, why="click the benchmark icon"
    )

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = wait_for_word(word="go", timeout=10, interval=1, why="start the benchmark")

    gui.moveTo(result["x"], result["y"])
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)


def run_benchmark():
    """Run cs2 benchmark"""
    setup_start_time = int(time.time())
    start_game()
    time.sleep(20)  # wait for game to load into main menu

    wait_for_word(
        word="play",
        why="verify that the game has loaded to the main menu",
    )

    identify_settings()

    navigate_settings()

    execute_benchmark()

    time.sleep(3)
    wait_for_word(word="benchmark", why="verify that the benchmark has started")

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    time.sleep(1)

    # Default fallback start time
    test_start_time = int(time.time())

    result = find_word(word="roll", timeout=30, interval=0.1)
    if result is None:
        logging.error("Didn't see 'lets roll'. Did the map load?")
    else:
        test_start_time = int(time.time())
        logging.info("Saw 'lets roll'! Marking the time.")

    time.sleep(112)  # sleep duration during gameplay

    # Default fallback end time
    test_end_time = int(time.time())

    wait_for_word(
        word="console",
        why="verify the console has opened to show the results",
    )

    test_end_time = int(time.time())
    user.press("`")
    logging.info("The console opened. Marking end time.")

    # allow time for result screen to populate
    time.sleep(13)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
    copy_artifact(CFG, ARTIFACTS_DIRECTORY)
    logging.info("Run completed. Closing game.")
    time.sleep(2)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


def main():
    """entry point to test script"""
    start_time, end_time = run_benchmark()

    height, width = get_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)


if __name__ == "__main__":
    try:
        setup_logging(LOG_DIRECTORY)
        main()
    except Exception as ex:
        logging.error("something went wrong running the benchmark!")
        logging.exception(ex)
        sys.exit(1)
    finally:
        terminate_process(PROCESS_NAME)
