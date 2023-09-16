from subprocess import Popen
import sys
import os
import logging
from shadow_of_the_tomb_raider_utils import get_resolution, templates

#pylint: disable=wrong-import-position
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import deprecated.cv2_utils
from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as steam_path 
#pylint: enable=wrong-import-position

STEAM_GAME_ID = 750920
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")


def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(steam_path + " " + steam_run_arg)
    return Popen([steam_path, steam_run_arg])


def clickOptions(options):
    """
    If the game is freshly installed the main menu has less options thus the options button
    looks different. We also account for if the options button is highlighted if the mouse
    is hovering over it.
    """
    if options is None or len(options) == 0:
        return

    try:
        deprecated.cv2_utils.wait_and_click(options[0], "graphics options", deprecated.cv2_utils.ClickType.HARD)
    except:
        clickOptions(options[1:])


def run_benchmark():
    """
    Start game via Steam and enter fullscreen mode
    """
    t1 = time.time()
    game_process = start_game()
    
    try:
        deprecated.cv2_utils.wait_and_click('load_menu_play', "play button", timeout=30)
    except:
        deprecated.cv2_utils.wait_and_click('load_menu_play_orange', "play button", timeout=30)

    """
    Wait for game to load and enter graphics submenu
    """
    optionImages = [
        'menu_options_save_game',
        'menu_options_save_game_highlighted',
        'menu_options',
        'menu_options_highlighted',
    ]
    clickOptions(optionImages)
    deprecated.cv2_utils.wait_and_click('menu_graphics', "graphics options", deprecated.cv2_utils.ClickType.HARD)
    time.sleep(2)  # let the menu transition
    screen = gui.screenshot(os.path.join(LOG_DIRECTORY, "display_settings.png"))
    deprecated.cv2_utils.wait_and_click('menu_graphics_tab', "graphics tab", deprecated.cv2_utils.ClickType.HARD)
    screen = gui.screenshot(os.path.join(LOG_DIRECTORY, "graphics_settings.png"))

    """
    Start the benchmark!
    """
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    user.press("r")
    start_time = time.time()

    """
    Wait for benchmark to complete
    """
    time.sleep(180)
    deprecated.cv2_utils.wait_for_image_on_screen('results_header', interval=2, timeout=60)
                        
    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")
    screen = gui.screenshot(os.path.join(LOG_DIRECTORY, "results.png"))

    # Exit
    terminate_processes("SOTTR")
    return start_time, end_time


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
        "graphics_preset": "current",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes("SOTTR")
    exit(1)
