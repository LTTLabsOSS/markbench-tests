from argparse import ArgumentParser
import logging
import os
import pydirectinput as user
import time
import sys
import pyautogui as gui
import re
import winreg

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.process import terminate_processes
from harness_utils.logging import setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT
from harness_utils.keras_service import KerasService


SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("APPDATA")

def WH_DIRECTORY() -> any:
    reg_path = r'Software\Microsoft\WIndows\CurrentVersion\Uninstall\Steam App 1142710'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, "InstallLocation")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

WARHAMMER_DIRECTORY = WH_DIRECTORY()
CONFIG_LOCATION = f"{APPDATA}\\The Creative Assembly\\Warhammer3\\scripts"
CONFIG_FILENAME = "preferences.script.txt"
PROCESS_NAME = "Warhammer3.exe"

user.FAILSAFE = False


def read_current_resolution():
    height_pattern = re.compile(r"y_res (\d+);")
    width_pattern = re.compile(r"x_res (\d+);")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg) as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)


def start_game():
    cmd_string = f"start /D \"{WARHAMMER_DIRECTORY}\" {PROCESS_NAME}"
    logging.info(cmd_string)
    return os.system(cmd_string)


def await_logo_screens(attempts: int) -> bool:
    logging.info("looking for logo")
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("warning")
        if result != None:
            return True
        time.sleep(5)

    return False


def skip_logo_screens() -> None:
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
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("options")
        if result != None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_advanced(attempts: int) -> any:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("ad")
        if result != None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_benchmark(attempts: int) -> any:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("bench")
        if result != None:
            return (result["x"], result["y"])
        time.sleep(1)

    return None


def find_summary(attempts: int) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("summary")
        if result != None:
            return True
        time.sleep(5)


def await_benchmark_start(attempts: int, delay=5) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word("fps")
        if result != None:
            return True
        time.sleep(delay)

    return None


def run_benchmark():
    start_game()
    t1 = time.time()
    time.sleep(5)

    logo_skip = await_logo_screens(10)
    if not logo_skip:
        logging.info("Did not warnings. Did the game start?")
        exit(1)

    skip_logo_screens()
    time.sleep(2)

    options = find_options(10)
    if not options:
        logging.info(
            "Did not find the options menu. Did the game skip the intros?")
        exit(1)

    gui.moveTo(options[0], options[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    advanced = find_advanced(10)

    if not advanced:
        logging.info(
            "Did not find the advanced menu. Did the game skip the intros?")
        exit(1)

    gui.moveTo(advanced[0], advanced[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    benchmark = find_benchmark(10)

    if not benchmark:
        logging.info(
            "Did not find the benchmark menu. Did the game skip the intros?")
        exit(1)

    gui.moveTo(benchmark[0], benchmark[1])
    time.sleep(0.2)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()

    time.sleep(2)

    user.press("enter")

    check_start = await_benchmark_start(5, 10)

    loading_screen_start = time.time()
    while (True):
        check_start = await_benchmark_start(2, 2)
        if check_start:
            break
        elif time.time()-loading_screen_start > 60:
            logging.info("Benchmark didn't start.")
            exit(1)
        logging.info("Benchmark hasn't started. Trying again in 10 seconds")
        time.sleep(10)

    t2 = time.time()
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()

    time.sleep(100)  # Wait for benchmark

    finish_benchmark = find_summary(250)

    if not finish_benchmark:
        logging.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?")
        exit(1)

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    # End the run
    end_time = time.time()
    logging.info(f"Benchmark took {round((end_time - start_time), 2)} seconds")

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
    result = {
        "resolution": f"{width}x{height}",
        "graphics_preset": "current",
        "start_time": round((start_time * 1000)),  # seconds * 1000 = millis
        "end_time": round((endtime * 1000))
    }

    write_report_json(LOG_DIRECTORY, "report.json", result)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    terminate_processes(PROCESS_NAME)
    exit(1)
