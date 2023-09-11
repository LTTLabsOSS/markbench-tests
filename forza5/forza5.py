import logging
from subprocess import Popen
import sys

from cv2_utils import * 
from forza5_utils import read_resolution

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.logging import *
from harness_utils.process import terminate_processes
from harness_utils.rtss import  start_rtss_process, copy_rtss_profile
from harness_utils.steam import get_run_game_id_command, DEFAULT_EXECUTABLE_PATH as steam_path 

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


def start_game():
    steam_run_arg = get_run_game_id_command(STEAM_GAME_ID)
    logging.info(steam_path + " " + steam_run_arg)
    return Popen([steam_path, steam_run_arg])


def run_benchmark():
    start_rtss()
    # Give RTSS time to start
    time.sleep(10)

    start_game()
    t1 = time.time()

    # Wait for menu to load
    time.sleep(60)

    user.press("x")
    time.sleep(2)
    
    try:
        wait_for_image_on_screen("accessibility", 0.70, 1, 5)
        user.press("escape")
        user.press("down")
        user.press("down")
        user.press("enter")
    except ImageNotFoundTimeout:
        pass


    wait_and_click("graphics", "graphics menu", ClickType.HARD)
    try:
        wait_and_click("benchmark_mode_pink", "run benchmark", ClickType.HARD)
    except:
        wait_and_click("benchmark_mode", "run benchmark", ClickType.HARD)

    time.sleep(1)
    user.press("down")
    user.press("enter")
    t2 = time.time()
    logging.info(f"Harness setup took {round((t2 - t1), 2)} seconds")
    start_time = time.time()

    time.sleep(110) # wait for benchmark to finish 95 seconds
    wait_for_image_on_screen("results", 0.70, 2, 60)
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
