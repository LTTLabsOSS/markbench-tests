import logging
import sys
from argparse import ArgumentParser
import os
import pydirectinput as user
import pyautogui as gui
import time 
from forza5_utils import read_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.output import *
from harness_utils.process import terminate_processes
from harness_utils.rtss import  start_rtss_process, copy_rtss_profile
from harness_utils.steam import exec_steam_run_command
from harness_utils.keras_service import KerasService

STEAM_GAME_ID = 1551360
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, "run")
APPDATALOCAL = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATALOCAL}\\ForzaHorizon5\\User_SteamLocalStorageDirectory\\ConnectedStorage\\ForzaUserConfigSelections"
CONFIG_FILENAME = "UserConfigSelections"
PROCESSES = ["ForzaHorizon5.exe", "RTSS.exe"]


def start_rtss():
    profile_path = os.path.join(SCRIPT_DIR, "ForzaHorizon5.exe.cfg")
    copy_rtss_profile(profile_path)
    return start_rtss_process()


def is_word_on_screen(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result != None:
            return True
        time.sleep(delay_seconds)
    return False

def is_word_clickable(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result != None:
            return (result["x"], result["y"])
        time.sleep(delay_seconds)

    return None

def accessibility() -> any:
    return is_word_on_screen(word="start", attempts=10, delay_seconds=1)

def graphics() -> any:
    return is_word_clickable(word="graphics", attempts=10, delay_seconds=1)

def benchmark() -> any:
    return is_word_clickable(word="benchmark", attempts=10, delay_seconds=1)

def results() -> any:
    return is_word_on_screen(word="results", attempts=25, delay_seconds=1)
    
def checkpoint() -> any:
    return is_word_on_screen(word="checkpoint", attempts=10, delay_seconds=1)


def run_benchmark():
    start_rtss()
    # Give RTSS time to start
    time.sleep(10)

    exec_steam_run_command(STEAM_GAME_ID)
    t1 = time.time()

    # Wait for menu to load
    time.sleep(30)
    menu_screen_wait = time.time()
    while (True):
        accessibility()
        if accessibility():
            start_time = time.time()
            logging.info("Accessibilty found pressing X to continue.")
            user.press("x")
            time.sleep(2)
            break
        elif time.time()-menu_screen_wait > 60:
            logging.info("Game didn't start.")
            exit(1)
        logging.info("Game hasn't started. Trying again in 10 seconds")
        time.sleep(10)

    graphics_wait = time.time()
    while (True):
        graphics()
        if graphics():
            logging.info("Graphics found, clicking and continuing.")
            graphics_click = graphics()
            gui.moveTo(graphics_click[0], graphics_click[1])
            time.sleep(0.2)
            gui.mouseDown()
            time.sleep(0.2)
            gui.mouseUp()
            time.sleep(1)
            break
        elif time.time()-graphics_wait > 60:
            logging.info("Game didn't load to the settings menu.")
            exit(1)
        logging.info("Menu hasn't loaded yet. Trying again in 10 seconds")
        time.sleep(10)

    if benchmark():
        logging.info("Benchmark found, clicking and starting benchmark.")
        benchmark_click = benchmark()
        gui.moveTo(benchmark_click[0], benchmark_click[1])
        time.sleep(0.2)
        gui.mouseDown()
        time.sleep(0.2)
        gui.mouseUp()
        time.sleep(1)
        user.press("down")
        time.sleep(0.2)
        user.press("enter")
        time.sleep(0.2)

    loading_screen_start = time.time()
    while (True):
        checkpoint()
        if checkpoint():
            break
        elif time.time()-loading_screen_start > 360:
            logging.info("Benchmark didn't start.")
            exit(1)
        logging.info("Benchmark hasn't started. Trying again in 10 seconds")
        time.sleep(10)

    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()

    time.sleep(95) # wait for benchmark to finish 95 seconds
    if results():
        logging.info("Results screen found. Ending run.")
        end_time = time.time()
    logging.info(f"Benchmark took {round((end_time - start_time), 2)} seconds")
    terminate_processes(*PROCESSES)
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
    start_time, end_time = run_benchmark()
    width, height = read_resolution(f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}")
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
    terminate_processes(*PROCESSES)
    exit(1)
