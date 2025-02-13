"""Cyberpunk 2077 test script"""
import time
import logging
import sys
import os
import pydirectinput as user
from cyberpunk_utils import copy_no_intro_mod, get_args, read_current_resolution


sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.output import (
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id
from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.misc import press_n_times

STEAM_GAME_ID = 1091500
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "cyberpunk2077.exe"


def start_game():
    """Launch the game with no launcher or start screen"""
    return exec_steam_game(STEAM_GAME_ID, game_params=["--launcher-skip", "-skipStartScreen"])


def navigate_to_settings():
    """navigate from main menu to settings menu"""
    logging.info("Navigating main menu")
    result = kerasService.look_for_word("continue", attempts=10)
    if not result:
        # an account with no save game has less menu options, so just press left and enter settings
        user.press("left")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)
    else:
        user.press("left")
        time.sleep(0.5)
        user.press("down")
        time.sleep(0.5)
        user.press("enter")
        time.sleep(0.5)

def check_for_rt():
    result = kerasService.wait_for_word("reflections", interval=1, timeout=2)
    if result:
        press_n_times("down", 3, 0.2)
        am.take_screenshot("graphics_rt.png", ArtifactType.CONFIG_IMAGE, "graphics menu rt")
    if not result:
        result = kerasService.wait_for_word("path", interval=1, timeout=2)
        if result:
            user.press("down")
            am.take_screenshot("graphics_pt.png", ArtifactType.CONFIG_IMAGE, "graphics menu path tracing")

def navigate_settings() -> None:
    """Simulate inputs to navigate the main menu"""
    navigate_to_settings()
    result = kerasService.wait_for_word("volume", interval=3, timeout=20)
    if not result:
        logging.info("Did not see the volume options. Did keras navigate to the settings menu correctly?")
        sys.exit(1)
    # entered settings
    user.press("3")
    time.sleep(0.5)
    user.press("3")
    time.sleep(0.5)
    user.press("3")
    time.sleep(0.5)

    result = kerasService.wait_for_word("preset", interval=3, timeout=20)
    if not result:
        logging.info("Did not see preset options. Did the game navigate to the graphics menu correctly?")
        sys.exit(1)
    # now on graphics tab
    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "graphics menu 1")

    result = kerasService.wait_for_word("DLSS", interval=1, timeout=2)
    if result:
        result = kerasService.wait_for_word("multi", interval=1, timeout=2)
        if result:
            user.press("down")
        press_n_times("down", 3, 0.2)
    
    result = kerasService.wait_for_word("AMD", interval=1, timeout=2)
    if result:
        press_n_times("down", 2, 0.2)
        
    result = kerasService.wait_for_word("Intel", interval=1, timeout=2)
    if result:
        press_n_times("down", 2, 0.2)

    else:
        user.press("down")

    check_for_rt()

    for _ in range(7):
        user.press("down")
        time.sleep(0.5)

    result = kerasService.wait_for_word("anisotropy", interval=3, timeout=20)
    if not result:
        logging.info("Did not see anisotropic options. Did the game navigate the graphics menu correctly?")
        sys.exit(1)
    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "graphics menu 2")

    for _ in range(11):
        user.press("down")
        time.sleep(0.5)

    result = kerasService.wait_for_word("occlusion", interval=3, timeout=20)
    if not result:
        logging.info("Did not see ambient occlusion options. Did the game navigate to the graphics menu correctly?")
        sys.exit(1)
    am.take_screenshot("graphics_3.png", ArtifactType.CONFIG_IMAGE, "graphics menu 3")

    for _ in range(3):
        user.press("down")
        time.sleep(0.5)

    result = kerasService.wait_for_word("level", interval=3, timeout=20)
    if not result:
        logging.info("Did not see LOD options. Did the game navigate to the graphics menu correctly?")
        sys.exit(1)
    am.take_screenshot("graphics_4.png", ArtifactType.CONFIG_IMAGE, "graphics menu 4")

    user.press("3")
    time.sleep(0.5)

    result = kerasService.wait_for_word("resolution", interval=3, timeout=20)
    if not result:
        logging.info("Did not see preset options. Did the game navigate to the graphics menu correctly?")
        sys.exit(1)
    # now on video tab
    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "video menu")

    user.press("b")
    time.sleep(0.5)
    user.press("enter")


def run_benchmark():
    """Start the benchmark"""
    copy_no_intro_mod()

    # Start game via Steam and enter fullscreen mode
    setup_start_time = time.time()
    start_game()

    time.sleep(20)

    result = kerasService.wait_for_word("new", interval=3, timeout=60)
    if not result:
        logging.info("Did not see settings menu option.")
        sys.exit(1)

    navigate_settings()

    # Start the benchmark!
    setup_end_time = time.time()
    elapsed_setup_time = round(setup_end_time - setup_start_time, 2)
    logging.info("Harness setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("fps", timeout=60, interval=0.2)
    if not result:
        logging.info("Benchmark didn't start.")
        sys.exit(1)

    test_start_time = time.time() - 5

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(60)
    result = kerasService.wait_for_word("results", timeout=240, interval=0.5)
    if not result:
        logging.info("Did not see results screen. Mark as DNF.")
        sys.exit(1)

    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark")

    test_end_time = time.time() - 2
    time.sleep(2)
    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)
    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(filename=f'{LOG_DIRECTORY}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

args = get_args()
kerasService = KerasService(args.keras_host, args.keras_port)
am = ArtifactManager(LOG_DIRECTORY)

try:
    start_time, end_time = run_benchmark()
    resolution = read_current_resolution()
    report = {
        "resolution": f"{resolution}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    am.create_manifest()
    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
