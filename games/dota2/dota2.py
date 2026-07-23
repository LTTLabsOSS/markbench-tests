"""Dota 2 test script"""

import logging
import sys
import time
from pathlib import Path

import pyautogui as gui
import pydirectinput as user
from dota2_utils import (
    copy_config,
    copy_replay,
    get_resolution,
    verify_replay,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import reset_artifacts, save_screenshot
from harness_utils.paths import harness_directories
from harness_utils.ocr_service import find_word
from harness_utils.report import format_resolution, seconds_to_milliseconds, write_report_json
from harness_utils.output_logging import setup_logging
from harness_utils.process import terminate_process
from harness_utils.steam import exec_steam_game

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "dota2.exe"
STEAM_GAME_ID = 570


setup_logging(LOG_DIRECTORY)

reset_artifacts(ARTIFACTS_DIRECTORY)

user.FAILSAFE = False


def start_game():
    """Launch the game with console enabled and FPS unlocked"""
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["-console", "+fps_max 0", "-novid"]
    )


def console_command(command):
    """Enter a console command"""
    gui.write(command)
    user.press("enter")


def harness_setup():
    """Copies the replay and config files to the appropriate spots"""
    verify_replay()
    copy_replay()
    copy_config()


def screenshot_settings():
    """Screenshots the settings for the game"""
    screen_height, screen_width = get_resolution()
    location = None
    click_multiple = 0
    # We check the resolution so we know which screenshot to use for the locate on screen function
    match screen_width:
        case "1280":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_720.png", confidence=0.9
            )
            click_multiple = 0.8
        case "1920":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1080.png", confidence=0.9
            )
            click_multiple = 1
        case "2560":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_1440.png", confidence=0.9
            )
            click_multiple = 1.5
        case "3840":
            location = gui.locateOnScreen(
                f"{SCRIPT_DIRECTORY}\\screenshots\\settings_2160.png", confidence=0.9
            )
            click_multiple = 2
        case _:
            logging.error(
                "Could not find the settings cog. The game resolution is currently %s, %s. Are you using a standard resolution?",
                screen_height,
                screen_width,
            )
            sys.exit(1)

    # navigating to the video config section
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    result = find_word(word="video", timeout=10, interval=1)
    if not result:
        logging.info(
            "Did not find the video menu button. Did OCR enter settings correctly?"
        )
        sys.exit(1)

    gui.moveTo(
        result["x"] + int(50 * click_multiple), result["y"] + int(20 * click_multiple)
    )
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)
    if find_word(word="resolution", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    save_screenshot(ARTIFACTS_DIRECTORY / "video1.png")

    user.press("down")

    if find_word(word="api", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    save_screenshot(ARTIFACTS_DIRECTORY / "video2.png")

    user.press("down")

    if find_word(word="direct", timeout=30, interval=1) is None:
        logging.info("Did not find the video settings menu. Did the menu get stuck?")
        sys.exit(1)

    save_screenshot(ARTIFACTS_DIRECTORY / "video3.png")


def load_the_benchmark():
    """Loads the replay and runs the benchmark"""
    user.press("escape")
    logging.info("Starting benchmark")
    user.press("\\")
    time.sleep(0.5)
    console_command("sv_cheats true")
    time.sleep(1)
    console_command("exec_async benchmark_load")
    time.sleep(5)
    if find_word(word="directed", timeout=30, interval=1) is None:
        logging.info("Did not find the directed camera. Did the replay load?")
        sys.exit(1)
    console_command("sv_cheats true")
    time.sleep(1)
    console_command("exec_async benchmark_run")
    user.press("\\")


def run_benchmark():
    """Run dota2 benchmark"""
    harness_setup()
    setup_start_time = int(time.time())
    start_game()
    time.sleep(10)  # wait for game to load into main menu

    # waiting about a minute for the main menu to appear
    if find_word(word="heroes", timeout=80, interval=1) is None:
        logging.error("Game didn't start in time. Check settings and try again.")
        sys.exit(1)

    time.sleep(15)  # wait for main menu
    screenshot_settings()

    # starting the benchmark
    load_the_benchmark()

    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)
    time.sleep(23)

    # Default fallback start time
    test_start_time = int(time.time())

    result = find_word(word="2560", timeout=30, interval=0.1)
    if result is None:
        logging.error("Unable to find Leshrac's HP. Using default start time value.")
    else:
        test_start_time = int(time.time())
        logging.info("Found Leshrac's HP! Marking the start time accordingly.")

    time.sleep(73)  # sleep duration during gameplay

    # Default fallback end time
    test_end_time = int(time.time())

    result = find_word(word="1195", timeout=30, interval=0.1)
    if result is None:
        logging.error(
            "Unable to find gold count of 1195. Using default end time value."
        )
    else:
        test_end_time = int(time.time())
        logging.info("Found the gold. Marking end time.")

    time.sleep(2)

    if find_word(word="heroes", timeout=25, interval=1) is None:
        logging.error("Main menu after running benchmark not found, exiting")
        sys.exit(1)

    time.sleep(4)
    logging.info("Run completed. Closing game.")

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    terminate_process(PROCESS_NAME)

    return test_start_time, test_end_time


try:
    start_time, end_time = run_benchmark()
    res_height, res_width = get_resolution()
    report = {
        "resolution": format_resolution(int(res_width), int(res_height)),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_process(PROCESS_NAME)
    sys.exit(1)
