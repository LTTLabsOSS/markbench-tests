"""Cyberpunk 2077 test script"""

import logging
import sys
import time
from pathlib import Path

import pydirectinput as user
from cyberpunk_utils import copy_no_intro_mod, read_current_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, press
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

STEAM_GAME_ID = 1091500
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "cyberpunk2077.exe"

user.FAILSAFE = False


def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["--launcher-skip", "-skipStartScreen"]
    )


def run_benchmark():
    """Start the benchmark"""
    copy_no_intro_mod()

    # Start game via Steam and enter fullscreen mode
    setup_start_time = int(time.time())
    start_game()

    time.sleep(20)

    result = find_word("new", interval=3, timeout=60)
    if not result:
        logging.info("Did not see settings menu option.")
        sys.exit(1)

    logging.info("Navigating main menu")
    result = find_word("continue", timeout=10)
    if not result:
        # an account with no save game has less menu options, so just press left and enter settings
        press("left, enter")
    else:
        press("left, down, enter")

    result = find_word("volume", interval=3, timeout=20)
    if not result:
        logging.info(
            "Did not see the volume options. Did the game navigate to the settings menu correctly?"
        )
        sys.exit(1)
    # entered settings
    press("3*3")

    result = find_word("preset", interval=3, timeout=20)
    if not result:
        logging.info(
            "Did not see preset options. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    # now on graphics tab
    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "graphics menu 1")

    press("down*2")  # gets you to film grain

    dlss = find_word("dlss", interval=1, timeout=2)
    if dlss:
        result = find_word("multi", interval=1, timeout=2)
        if result:
            user.press("down")
        press(
            "down*2", pause=0.2
        )  # gets you to film grain usually except for combined with RT
        result = find_word("grain", interval=1, timeout=2)
        if not result:
            user.press("down")

    fsr = find_word("amd", interval=1, timeout=2)
    if fsr:
        user.press("down")  # gets you to film grain

    xess = find_word("intel", interval=1, timeout=2)
    if xess:
        user.press("down")  # gets you to film grain

    result = find_word("reflections", interval=1, timeout=2)
    if result:
        press("down*3", pause=0.2)
        am.take_screenshot(
            "graphics_rt.png", ArtifactType.CONFIG_IMAGE, "graphics menu rt"
        )
    if not result:
        result = find_word("path", interval=1, timeout=2)
        if result:
            user.press("down")
            am.take_screenshot(
                "graphics_pt.png",
                ArtifactType.CONFIG_IMAGE,
                "graphics menu path tracing",
            )

    press("down*7")

    for _ in range(10):
        if find_word("anisotropy", interval=1, timeout=5):
            break
        press("down")
    else:
        logging.info(
            "Max attempts reached for checking the camera. Did the game load the save?"
        )
        sys.exit(1)

    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "graphics menu 2")

    press("down*11")

    result = find_word("occlusion", interval=3, timeout=20)
    if not result:
        logging.info(
            "Did not see ambient occlusion options. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    am.take_screenshot("graphics_3.png", ArtifactType.CONFIG_IMAGE, "graphics menu 3")

    press("down*3")

    result = find_word("level", interval=3, timeout=20)
    if not result:
        logging.info(
            "Did not see LOD options. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    am.take_screenshot("graphics_4.png", ArtifactType.CONFIG_IMAGE, "graphics menu 4")

    press("3")

    result = find_word("resolution", interval=3, timeout=20)
    if not result:
        logging.info(
            "Did not see preset options. Did the game navigate to the graphics menu correctly?"
        )
        sys.exit(1)
    # now on video tab
    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "video menu")

    press("b")
    user.press("enter")

    # Start the benchmark!
    setup_end_time = int(time.time())
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    result = find_word("fps", timeout=60, interval=0)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = int(time.time()) - 5

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(60)
    result = find_word("results", timeout=240, interval=1)
    if not result:
        logging.info("Did not see results screen. Mark as DNF.")
        sys.exit(1)

    am.take_screenshot(
        "results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark"
    )

    test_end_time = int(time.time()) - 2
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_logging(LOG_DIRECTORY)

am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID),
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
