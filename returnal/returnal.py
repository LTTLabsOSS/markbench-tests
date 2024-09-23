"""Returnal test script"""
import os
import logging
import sys
import time
import pydirectinput as user

from returnal_utils import get_resolution, get_args

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
from harness_utils.misc import remove_files
from harness_utils.process import terminate_processes
from harness_utils.steam import (
  exec_steam_run_command,
  get_steamapps_common_path,
)

STEAM_GAME_ID = 1649240
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "Returnal"
LOCAL_USER_SETTINGS = os.path.join(
  os.getenv('LOCALAPPDATA'), "Returnal", "Steam",
  "Saved", "Config", "WindowsNoEditor", "GameUserSettings.ini"
  )
VIDEO_PATH = os.path.join(get_steamapps_common_path(), "Returnal", "Returnal", "Content", "Movies")

user.FAILSAFE = False

intro_videos = [
    os.path.join(VIDEO_PATH, "Logos_PC.mp4"),
    os.path.join(VIDEO_PATH, "Logos_PC_UW21.mp4"),
    os.path.join(VIDEO_PATH, "Logos_PC_UW32.mp4"),
    os.path.join(VIDEO_PATH, "Logos_Short_PC.mp4"),
    os.path.join(VIDEO_PATH, "Logos_Short_PC_UW21.mp4"),
    os.path.join(VIDEO_PATH, "Logos_Short_PC_UW32.mp4"),
]

def check_vram_alert(attempts: int) -> bool:
    """Look for VRAM alert in menu"""
    logging.info("Checking for VRAM alert prompt")
    for _ in range(attempts):
        alert_result = kerasService.capture_screenshot_find_word("alert")
        locate_result = kerasService.capture_screenshot_find_word("locate")
        if locate_result is not None:
            return False
        if alert_result is not None:
            return True
        time.sleep(2)

    return False


def escape_vram_alert():
    """Navigate VRAM alert"""
    user.keyDown("space")
    time.sleep(4)
    user.keyUp("space")


def navigate_options_menu() -> None:
    """Simulate inputs to navigate to options menu"""
    logging.info("Navigating to options menu")
    user.press("esc")
    time.sleep(0.2)
    user.press("enter")
    time.sleep(0.2)
    user.press("q")
    time.sleep(0.2)
    user.keyDown("tab")
    time.sleep(5)
    user.keyUp("tab")


def run_benchmark() -> tuple[float]:
    """Run the benchmark"""
    logging.info("Removing intro videos")
    remove_files(intro_videos)

    logging.info("Starting game")
    exec_steam_run_command(STEAM_GAME_ID)
    setup_start_time = time.time()

    time.sleep(10)

    # Check if GPU has too little v ram and skip alert
    alert_found = check_vram_alert(7)

    if alert_found:
        escape_vram_alert()

    # Make sure the game started correctly
    result = kerasService.look_for_word("locate", 10, 5)
    if not result:
        logging.info("Could not find prompt to open menu!")
        sys.exit(1)

    # Navigate to in-game benchmark and start it
    navigate_options_menu()

    setup_end_time = time.time()
    elapsed_setup_time = round((setup_end_time - setup_start_time), 2)
    logging.info("Setup took %s seconds", elapsed_setup_time)

    result = kerasService.wait_for_word("performance", interval=0.2, timeout=30)
    if not result:
        logging.info(
            "Performance graph was not found! Could not mark the start time.")
        sys.exit(1)

    test_start_time = time.time()

    # Wait for benchmark to complete
    time.sleep(112)

    # Wait for results screen to display info
    result = kerasService.wait_for_word("lost", interval=0.1, timeout=11)
    if not result:
        logging.info(
            "Didn't see signal lost. Could not mark the proper end time!")

    test_end_time = round(time.time() - 2)

    result = kerasService.wait_for_word("benchmark", interval=0.5, timeout=15)
    if not result:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    elapsed_test_time = round((test_end_time - test_start_time), 2)
    logging.info("Benchmark took %s seconds", elapsed_test_time)

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

try:
    start_time, end_time = run_benchmark()
    height, width = get_resolution(LOCAL_USER_SETTINGS)
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
