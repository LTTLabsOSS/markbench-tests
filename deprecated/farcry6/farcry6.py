import os
from subprocess import Popen
import logging
import time
import pydirectinput as user
import sys

from cv2_utils import *
from far_cry_6_utils import get_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.logging import *
from harness_utils.process import terminate_processes

DEFAULT_INSTALLATION_PATH = "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\games\\Far Cry 6\\bin"
EXECUTABLE = "FarCry6.exe"
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
PROCESS_NAME = "FarCry6"


def start_game():
    cmd = DEFAULT_INSTALLATION_PATH + '\\' + EXECUTABLE
    logging.info(cmd)
    return Popen(cmd)


def run_benchmark():
    start_game()
    t1 = time.time()

    time.sleep(50)

    user.press("space")
    user.press("space")

    wait_and_click('options', 'options button', click_type=ClickType.HARD)
    time.sleep(2)
    wait_and_click('benchmark', 'options button', click_type=ClickType.HARD)

    t2 = time.time()
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")

    start_time = time.time()

    time.sleep(75) # wait for benchmark to complete 60 + 15 grace
    wait_for_image_on_screen('header', 'results', interval=2, timeout=60)

    end_time = time.time()
    logging.info(f"Benchark took {round((end_time - start_time), 2)} seconds")

    # Exit
    terminate_processes(PROCESS_NAME)
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
    start_time, end_time = run_benchmark()
    height, width = get_resolution()
    result = {
        "resolution": format_resolution(width, height),
        "graphics_preset": "current",
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time)
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    exit(1)