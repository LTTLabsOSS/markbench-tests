"""Hitman World of Assassination test script"""
import os
import logging
import time
import psutil
import pyautogui as gui
import sys
import winreg

from hitman3_utils import get_resolution, get_args, process_registry_file, get_benchmark_name

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from harness_utils.ocr_service import OCRService
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_DATE_FORMAT,
)
from harness_utils.steam import (
  exec_steam_run_command,
  get_build_id
)
from harness_utils.artifacts import ArtifactManager, ArtifactType

STEAM_GAME_ID = 1659040
STEAM_PATH = os.path.join(os.environ["ProgramFiles(x86)"], "steam")
STEAM_EXECUTABLE = "steam.exe"
PROCESS_NAMES = ['HITMAN3.exe', 'Launcher.exe']
script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, "run")

input_file = os.path.join(script_dir, 'graphics.reg')
config_file = os.path.join(script_dir, 'graphics_config.txt')
hive = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\\IO Interactive\\HITMAN3"

def benchmark_check():
    benchmark_id = get_benchmark_name(config_file)
    if benchmark_id == 0:
        benchmark_name = "Hitman World of Assassination: Dubai"
        benchmark_time = 102
    elif benchmark_id == 1:
        benchmark_name = "Hitman World of Assassination: Dartmoor"
        benchmark_time = 140
    else:
        raise ValueError("Could not determine the benchmark. Is there an error in the registry?")
    
    return benchmark_name, benchmark_time


def run_benchmark():
    setup_start_time = int(time.time())
    am = ArtifactManager(log_dir)
    process_registry_file(hive, SUBKEY, input_file, config_file)
    am.copy_file(config_file, ArtifactType.CONFIG_TEXT, "config file")
    benchmark_name, benchmark_time = benchmark_check()
    exec_steam_run_command(STEAM_GAME_ID)

    time.sleep(2)
    location = gui.locateOnScreen(f"{script_dir}\\screenshots\\options.png", confidence=0.7) #luckily this seems to be a set resolution for the button
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(2)

    am.take_screenshot("Options1.png", ArtifactType.CONFIG_IMAGE, "1st picture of options")
    time.sleep(1)
    gui.scroll(-1000)
    am.take_screenshot("Options2.png", ArtifactType.CONFIG_IMAGE, "2nd picture of options")
    time.sleep(2)

    

    location = gui.locateOnScreen(f"{script_dir}\\screenshots\\start_benchmark.png", confidence=0.7) #luckily this seems to be a set resolution for the button
    click_me = gui.center(location)
    gui.moveTo(click_me.x, click_me.y)
    gui.mouseDown()
    time.sleep(0.2)
    gui.mouseUp()
    time.sleep(0.2)

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logging.info("Setup took %f seconds", elapsed_setup_time)

    time.sleep(5)

    result = kerasService.look_for_word("crowd", attempts=20, interval=1)
    if not result:
        logging.info("Did not find the statistics in the corner. Did the benchmark launch?")
        raise RuntimeError("Benchmark failed.")

    test_start_time = int(time.time())
  
    time.sleep(benchmark_time) # sleep during the benchmark which is indicated based on the benchmark detected.
    
    result = kerasService.look_for_word("overall", attempts=20, interval=1)
    if not result:
        logging.info("Did not find the overall FPS score. Did the benchmark crash?")
        raise RuntimeError("Benchmark failed.")

    test_end_time = int(time.time()) - 1
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logging.info("Benchmark took %f seconds", elapsed_test_time)
    am.take_screenshot("results.png", ArtifactType.RESULTS_IMAGE, "benchmark results")
    time.sleep(1)

    for proc in psutil.process_iter():
        try:
            if proc.name() in PROCESS_NAMES:
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignore processes that no longer exist or cannot be accessed

    am.create_manifest()
    return test_start_time, test_end_time, benchmark_name


setup_log_directory(log_dir)

logging.basicConfig(filename=f'{log_dir}/harness.log',
                    format=DEFAULT_LOGGING_FORMAT,
                    datefmt=DEFAULT_DATE_FORMAT,
                    level=logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

args = get_args()
kerasService = OCRService(args.keras_host, args.keras_port)

try:
    test_start_time, test_end_time, benchmark_name = run_benchmark()
    height, width = get_resolution(config_file)
    report = {
        "resolution": f"{width}x{height}",
        "benchmark": benchmark_name,
        "start_time": seconds_to_milliseconds(test_start_time), # seconds * 1000 = millis
        "end_time": seconds_to_milliseconds(test_end_time),
        "version": get_build_id(STEAM_GAME_ID)
    }

    write_report_json(log_dir, "report.json", report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    for proc in psutil.process_iter():
        try:
            if proc.name() in PROCESS_NAMES:
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignore processes that no longer exist or cannot be accessed

    exit(1)