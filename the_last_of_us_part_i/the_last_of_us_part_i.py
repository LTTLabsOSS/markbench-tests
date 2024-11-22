"""The Last of Us Part I test script"""
import logging
import os
import time
import sys
import pydirectinput as user

from the_last_of_us_part_i_utils import get_args, get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.keras_service import KerasService
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import (
  get_registry_active_user,
  exec_steam_run_command,
)
from harness_utils.misc import press_n_times

from harness_utils.artifacts import ArtifactManager, ArtifactType

STEAM_GAME_ID = 1888930
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "tlou"

user.FAILSAFE = False

def take_screenshots(am: ArtifactManager) -> None:
    """Take screenshots of the benchmark settings"""
    logging.info("Taking screenshots of benchmark settings")
    press_n_times("s",2,0.2 )
    user.press("enter")
    press_n_times("s",4,0.2 )
    user.press("enter")
    am.take_screenshot("video1.png", ArtifactType.CONFIG_IMAGE, "screenshot of video settings1")

    press_n_times("s",15,0.2)
    am.take_screenshot("video2.png", ArtifactType.CONFIG_IMAGE, "screenshot of video settings2")

    press_n_times("s",6, 0.2)
    am.take_screenshot("video3.png", ArtifactType.CONFIG_IMAGE, "screenshot of video settings3")

    user.press("backspace")
    user.press("s")
    user.press("enter")
    am.take_screenshot("graphics1.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings1")
    press_n_times("s", 10, 0.2)
    am.take_screenshot("graphics2.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings2")
    press_n_times("s", 7, 0.2)
    am.take_screenshot("graphics3.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings3")
    press_n_times("s", 9, 0.2)
    am.take_screenshot("graphics4.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings4")
    press_n_times("s", 7, 0.2)
    am.take_screenshot("graphics5.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings5")
    press_n_times("s", 6, 0.2)
    am.take_screenshot("graphics6.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings6")
    press_n_times("s", 5, 0.2)
    am.take_screenshot("graphics7.png", ArtifactType.CONFIG_IMAGE, "screenshot of graphics settings7")
    user.press("backspace")
    user.press("backspace")
    press_n_times("w", 2, 0.2)

def navigate_main_menu(am: ArtifactManager) -> None:
    """Input to navigate main menu"""
    logging.info("Navigating main menu")

    # Enter TLOU menu
    user.press("space")
    time.sleep(0.5)
    take_screenshots(am)

    user.press("space")
    time.sleep(0.5)
    # Press load game
    user.press("s")
    time.sleep(0.5)
    user.press("s")
    time.sleep(0.5)
    user.keyDown("space")
    time.sleep(0.5)
    # Go to bottom save
    user.press("w")
    time.sleep(0.5)
    user.press("space")
    time.sleep(0.5)
    user.press("space")
    time.sleep(2)


def run_benchmark():
    """Starts the benchmark"""
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()
    am = ArtifactManager(LOG_DIRECTORY)
    time.sleep(10)

    result = kerasService.wait_for_word("press", interval=3, timeout=60)
    if not result:
        logging.info("Did not see start screen")
        sys.exit(1)

    navigate_main_menu(am)

    # press load save
    result = kerasService.look_for_word("yes", attempts=10, interval=1)
    if not result:
        logging.info("Did not load the save")
        sys.exit(1)

    user.press("a")
    time.sleep(0.5)
    user.press("space")

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("tommy", interval=0.2, timeout=250)
    if not result:
        logging.info("Did not see Tommy's first subtitle. Did the game load?")
        sys.exit(1)
    test_start_time = time.time()
    logging.info("Saw Tommy's first line. Benchmark has started.")

    # wait for black screen
    time.sleep(150)

    # This actually looks for "from?" but the current ML model sees it as fromy
    result = kerasService.wait_for_word("fromy", interval=0.2, timeout=250)
    if not result:
        logging.info("Did not find prompt to end harness.")
        sys.exit(1)

    # Wait for black screen
    time.sleep(24)

    test_end_time = time.time()

    time.sleep(2)
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    time.sleep(3)

    terminate_processes(PROCESS_NAME)

    am.create_manifest()

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

try:
    start_time, end_time = run_benchmark()
    steam_id = get_registry_active_user()
    config_path = os.path.join(
        os.environ["HOMEPATH"], "Saved Games" ,"The Last of Us Part I",
        "users", str(steam_id), "screeninfo.cfg"
    )
    height, width = get_resolution(config_path)
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
