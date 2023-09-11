from argparse import ArgumentParser
import logging
import os
import pydirectinput as user
import time
from subprocess import Popen
import sys
from utils import read_resolution, remove_intros, skippable

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as STEAM_PATH
from harness_utils.process import terminate_processes
from harness_utils.logging import setup_log_directory, write_report_json, DEFAULT_LOGGING_FORMAT, DEFAULT_DATE_FORMAT
from harness_utils.keras_service import KerasService

STEAM_GAME_ID = 668580
SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "run")
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\AtomicHeart\\Saved\\Config\\WindowsNoEditor"
CONFIG_FILENAME = "GameUserSettings.ini"
PROCESS_NAME = "AtomicHeart"

user.FAILSAFE = False

def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(STEAM_PATH + " " + steam_run_arg)
    return Popen([STEAM_PATH, steam_run_arg])


def is_word_on_screen(word: str, attempts: int = 5, delay_seconds: int = 1) -> bool:
    for _ in range(attempts):
        result = kerasService.capture_screenshot_find_word(word)
        if result != None:
            return True
        time.sleep(delay_seconds)
    return False

def start_screen() -> any:
    return is_word_on_screen(word="press", attempts=20, delay_seconds=1)

def new_game() -> any:
    return is_word_on_screen(word="new", attempts=20, delay_seconds=1)

def check_menu_continue() -> any:
    return is_word_on_screen(word="continue", attempts=20, delay_seconds=1)

def await_space_to_start() -> any:
    return is_word_on_screen(word="cont", attempts=20, delay_seconds=1)

def await_wicked() -> any:
    return is_word_on_screen(word="wicked", attempts=250, delay_seconds=0.1)



def run_benchmark():
    remove_intros(skippable)
    start_game()
    t1 = time.time()

    time.sleep(10)

    if start_screen():
        user.press("space")

    if not start_screen():
        logging.info("Did not see start screen")
        exit(1)

    if new_game():
        if check_menu_continue():
            logging.info("Continue option available, navigating accordingly.")
            user.press("s")
            time.sleep(0.5)
            user.press("d")
            time.sleep(0.5)
            user.press("f")
            time.sleep(0.5)
            user.press("space")
        else:
            logging.info(
                "Continue option not available, navigating accordingly.")
            user.press("d")
            time.sleep(0.5)
            user.press("f")
            time.sleep(0.5)
            user.press("space")

    time.sleep(10)

    loading_screen= time.time()
    while (True):
        await_space_to_start()
        if await_space_to_start:
            logging.info("Continue found. Continuing Run.")
            user.press("space")           
            time.sleep(5)
            break
        elif time.time()-loading_screen>60:
            logging.info("Did not see the option to continue. Check settings and try again.")
            exit(1)
        logging.info("Game hasn't loaded. Trying again in 5 seconds")
        time.sleep(5)

    

    t2 = time.time()
    logging.info(f"Setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()

    time.sleep(230)  # wait for No Rest For the Wicked Quest

    # This looks for wicked
    wicked_check= time.time()
    while (True):
        await_wicked()
        if await_wicked:
            logging.info("Wicked found. Ending Benchmark.")           
            time.sleep(5)
            break
        elif time.time()-wicked_check>250:
            logging.info("Wicked was not found! Did harness not wait long enough? Or test was too long?")
            exit(1)
        logging.info("Game hasn't finished the opening sequence. Trying again in 5 seconds")
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
    height, width = read_resolution()
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
