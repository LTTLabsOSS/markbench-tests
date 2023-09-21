"""Shadow of the Tomb Raider test script"""
import os
import logging
import time
import sys
import pydirectinput as user
import pyautogui as gui
from shadow_of_the_tomb_raider_utils import get_resolution, templates

sys.path.insert(1, os.path.join(sys.path[0], '..'))
#pylint: disable=wrong-import-position
import deprecated.cv2_utils
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command
#pylint: enable=wrong-import-position

STEAM_GAME_ID = 750920
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")


def click_options(options):
    """
    If the game is freshly installed the main menu has less options thus the options button
    looks different. We also account for if the options button is highlighted if the mouse
    is hovering over it.
    """
    if options is None or len(options) == 0:
        return

    try:
        deprecated.cv2_utils.wait_and_click(
            options[0], "graphics options", deprecated.cv2_utils.ClickType.HARD)
    except deprecated.cv2_utils.ImageNotFoundTimeout:
        click_options(options[1:])


def run_benchmark():
    """Start game via Steam and enter fullscreen mode"""
    setup_start_time = time.time()
    exec_steam_run_command(STEAM_GAME_ID)

    try:
        deprecated.cv2_utils.wait_and_click('load_menu_play', "play button", timeout=30)
    except deprecated.cv2_utils.ImageNotFoundTimeout:
        deprecated.cv2_utils.wait_and_click('load_menu_play_orange', "play button", timeout=30)

    # Wait for game to load and enter graphics submenu
    option_images = [
        'menu_options_save_game',
        'menu_options_save_game_highlighted',
        'menu_options',
        'menu_options_highlighted',
    ]
    click_options(option_images)
    deprecated.cv2_utils.wait_and_click('menu_graphics', "graphics options", deprecated.cv2_utils.ClickType.HARD)
    time.sleep(2)  # let the menu transition
    gui.screenshot(os.path.join(LOG_DIRECTORY, "display_settings.png"))
    deprecated.cv2_utils.wait_and_click('menu_graphics_tab', "graphics tab", deprecated.cv2_utils.ClickType.HARD)
    gui.screenshot(os.path.join(LOG_DIRECTORY, "graphics_settings.png"))

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    user.press("r")
    test_start_time = time.time()

    # Wait for benchmark to complete
    time.sleep(180)
    deprecated.cv2_utils.wait_for_image_on_screen('results_header', interval=2, timeout=60)

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    gui.screenshot(os.path.join(LOG_DIRECTORY, "results.png"))

    # Exit
    terminate_processes("SOTTR")
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

try:
    deprecated.cv2_utils.templates = templates
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    result = {
        "resolution": f"{width}x{height}",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
#pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("SOTTR")
    sys.exit(1)
