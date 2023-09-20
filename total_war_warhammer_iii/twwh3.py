"""Total War: Warhammer III test script"""
from argparse import ArgumentParser
import logging
import os
import time
import sys
import re
import winreg
import pyautogui as gui
import pydirectinput as user

sys.path.insert(1, os.path.join(sys.path[0], '..'))
# pylint: disable=wrong-import-position
from harness_utils.process import terminate_processes
from harness_utils.output import (
    format_resolution,
    setup_log_directory,
    write_report_json,
    seconds_to_milliseconds,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT
)
from harness_utils.keras_service import KerasService
# pylint: enable=wrong-import-position

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("APPDATA")
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Warhammer3\\scripts"
CONFIG_FILENAME = "preferences.script.txt"
PROCESS_NAME = "Warhammer3.exe"

user.FAILSAFE = False

def get_directory() -> any:
    """Gets directory from registry key"""
    reg_path = r'Software\Microsoft\WIndows\CurrentVersion\Uninstall\Steam App 1142710'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def read_current_resolution():
    """Reads resolutions settings from local game file"""
    height_pattern = re.compile(r"y_res (\d+);")
    width_pattern = re.compile(r"x_res (\d+);")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height_value = 0
    width_value = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height_value = height_match.group(1)
            if width_match is not None:
                width_value = width_match.group(1)
    return (height_value, width_value)


def start_game():
    """Starts the game process"""
    cmd_string = f"start /D \"{get_directory()}\" {PROCESS_NAME}"
    logging.info(cmd_string)
    return os.system(cmd_string)


def await_logo_screens(attempts: int) -> bool:
    """Waits for logo screen"""
    logging.info("looking for logo")
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("warning")
        if result is not None:
            return True
        time.sleep(5)

    return False


def skip_logo_screens() -> None:
    """Simulate input to skip logo screens"""
    logging.info("Skipping logo screens")

    # Enter TWWH3 menu
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)
    user.press("escape")
    time.sleep(0.5)


def find_options(attempts: int) -> any:
    """Find options text"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("options")
        if result is not None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_advanced(attempts: int) -> any:
    """Find advanced text"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("ad")
        if result is not None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_benchmark(attempts: int) -> any:
    """Find benchmark options"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("bench")
        if result is not None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_summary(attempts: int) -> bool:
    """Find benchmark results"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("summary")
        if result is not None:
            return True
        time.sleep(5)


def await_benchmark_start(attempts: int, delay=5) -> bool:
    """Wait for benchmark to start"""
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("fps")
        if result is not None:
            return True
        time.sleep(delay)

    return None


def run_benchmark():
    """Starts the benchmark"""
    start_game()
    setup_start_time = time.time()
    time.sleep(5)

    logo_skip = await_logo_screens(10)
    if not logo_skip:
        logging.info("Did not warnings. Did the game start?")
        sys.exit(1)

    skip_logo_screens()
    time.sleep(2)

    options = find_options(10)
    if not options:
        logging.info(
            "Did not find the options menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(options[0], options[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    advanced = find_advanced(10)

    if not advanced:
        logging.info(
            "Did not find the advanced menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(advanced[0], advanced[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    benchmark = find_benchmark(10)

    if not benchmark:
        logging.info(
            "Did not find the benchmark menu. Did the game skip the intros?")
        sys.exit(1)

    gui.moveTo(benchmark[0], benchmark[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    time.sleep(2)

    user.press("enter")

    check_start = await_benchmark_start(5, 10)

    loading_screen_start = time.time()
    while True:
        check_start = await_benchmark_start(2, 2)
        if check_start:
            break
        if time.time()-loading_screen_start > 60:
            logging.info("Benchmark didn't start.")
            sys.exit(1)
        logging.info("Benchmark hasn't started. Trying again in 10 seconds")
        time.sleep(10)

    elapsed_setup_time = round(time.time() - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)
    test_start_time = time.time()

    time.sleep(100)  # Wait for benchmark

    finish_benchmark = find_summary(250)

    if not finish_benchmark:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        sys.exit(1)

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    # End the run
    test_end_time = time.time()
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
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

parser = ArgumentParser()
parser.add_argument("--kerasHost", dest="keras_host",
                    help="Host for Keras OCR service", required=True)
parser.add_argument("--kerasPort", dest="keras_port",
                    help="Port for Keras OCR service", required=True)
args = parser.parse_args()
kerasService = KerasService(args.keras_host, args.keras_port, os.path.join(
    LOG_DIRECTORY, "screenshot.jpg"))

try:
    start_time, endtime = run_benchmark()
    height, width = read_current_resolution()
    report = {
        "resolution": format_resolution(width, height),
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(endtime)
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
#pylint: disable=broad-exception-caught
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    sys.exit(1)
