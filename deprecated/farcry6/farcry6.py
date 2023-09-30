"""FarCry 6 test script"""
import logging
import os
import sys
import time
from subprocess import Popen

import pydirectinput as user
from far_cry_6_utils import get_resolution, templates

sys.path.insert(1, os.path.join(sys.path[0], ".."))
# pylint: disable=wrong-import-position
import deprecated.cv2_utils
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    format_resolution,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)
from harness_utils.process import terminate_processes

# pylint: enable=wrong-import-position

DEFAULT_INSTALLATION_PATH = (
    "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\games\\Far Cry 6\\bin"
)
EXECUTABLE = "FarCry6.exe"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "FarCry6"


def start_game():
    """Starts the game process"""
    cmd = DEFAULT_INSTALLATION_PATH + "\\" + EXECUTABLE
    logging.info(cmd)
    return Popen(cmd)


def run_benchmark():
    """Starts the benchmark"""
    start_game()
    setup_start_time = time.time()

    time.sleep(50)

    user.press("space")
    user.press("space")

    deprecated.cv2_utils.wait_and_click(
        "options", "options button", click_type=deprecated.cv2_utils.ClickType.HARD
    )
    time.sleep(2)
    deprecated.cv2_utils.wait_and_click(
        "benchmark", "options button", click_type=deprecated.cv2_utils.ClickType.HARD
    )

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    test_start_time = time.time()

    time.sleep(75)  # wait for benchmark to complete 60 + 15 grace
    deprecated.cv2_utils.wait_for_image_on_screen(
        "header", "results", interval=2, timeout=60
    )

    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    terminate_processes(PROCESS_NAME)
    return test_start_time, test_end_time


setup_log_directory(LOG_DIRECTORY)

logging.basicConfig(
    filename=f"{LOG_DIRECTORY}/harness.log",
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG,
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

try:
    deprecated.cv2_utils.templates = templates
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    result = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
# pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
