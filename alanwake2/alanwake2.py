"""Alan Wake 2 test script."""

import logging
import sys
import time
from pathlib import Path
from subprocess import Popen

from alanwake2_utils import CONFIG_PATH, copy_save, find_epic_executable, get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.misc import find_eg_game_version
from harness_utils.output import setup_logging, write_report_json
from harness_utils.process import terminate_processes

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "alanwake2.exe"
EXECUTABLE_PATH = find_epic_executable()
GAME_ID = "c4763f236d08423eb47b4c3008779c84%3A93f2a8c3547846eda966cb3c152a026e%3Adc9d2e595d0e4650b35d659f90d41059?action=launch&silent=true"
GAMEFOLDERNAME = "AlanWake2"


def get_run_game_id_command(game_id: int) -> str:
    return "com.epicgames.launcher://apps/" + str(game_id)


def launch_game() -> None:
    copy_save()
    cmd_string = get_run_game_id_command(GAME_ID)
    logging.info("%s %s", EXECUTABLE_PATH, cmd_string)
    Popen([EXECUTABLE_PATH, cmd_string])


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(10)

    if not find_word("saving", timeout=30, interval=1, msg="Game didn't start in time. Check settings and try again."):
        return FAILED_RUN
    press("enter")
    if not find_word("warning", timeout=30, interval=1, msg="Game didn't start in time. Check settings and try again."):
        return FAILED_RUN
    press("enter")
    if not find_word("continue", timeout=30, interval=1, msg="Game didn't start in time. Check settings and try again."):
        return FAILED_RUN
    press("enter")

    if find_word("house", timeout=10, interval=0.5):
        press("esc")
    if not find_word("load", timeout=5, interval=1, msg="Load game option does not exist. Did the save get copied correctly?"):
        return FAILED_RUN

    logging.info("Navigating to options to get some screenshots")
    press("down*4, enter")
    if not find_word("graphics", timeout=60, interval=0.5, msg="Graphics options not available. Did it navigate to the options correctly?"):
        return FAILED_RUN
    press("e*2")
    if not find_word("quality", timeout=60, interval=0.5, msg="Did not see quality preset. Did it navigate to graphics correctly?"):
        return FAILED_RUN
    am.take_screenshot("01_graphics_1.png", ArtifactType.CONFIG_IMAGE)
    press("down*19")
    if not find_word("terrain", timeout=60, interval=0.5, msg="Did not see Terrain Quality. Did it navigate to graphics correctly?"):
        return FAILED_RUN
    am.take_screenshot("02_graphics_2.png", ArtifactType.CONFIG_IMAGE)
    press("down*10")
    if not find_word("transparency", timeout=60, interval=0.5, msg="Did not see Transparency. Did it navigate to graphics correctly?"):
        return FAILED_RUN
    am.take_screenshot("03_graphics_3.png", ArtifactType.CONFIG_IMAGE)
    press("esc")

    logging.info("Seen the main menu. Loading benchmark.")
    press("up*3, enter")
    time.sleep(2)
    if not find_word("heart", timeout=60, interval=0.5, msg="Heart not showing in loadable games. Did the save get copied correctly?"):
        return FAILED_RUN
    press("right*3, enter")
    logging.info("Harness setup took %f seconds", round(int(time.time()) - setup_start_time, 2))

    if not find_word("recap", timeout=60, interval=0.5, msg="Didn't see the word recap. Did the save game load?"):
        return FAILED_RUN
    test_start_time = int(time.time())
    time.sleep(170)
    if not find_word("insane", timeout=60, interval=0.5, msg="Didn't see the word insane. Did the game crash?"):
        return FAILED_RUN
    test_end_time = int(time.time())
    time.sleep(2)
    am.copy_file(CONFIG_PATH, ArtifactType.CONFIG_TEXT, "renderer.ini")
    logging.info("Benchmark took %f seconds", round((test_end_time - test_start_time), 2))
    return test_start_time, test_end_time


def main() -> None:
    """Run the Alan Wake 2 benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = get_resolution()
            report = {
                "resolution": f"{width}x{height}",
                "start_time": round((start_time * 1000)),
                "end_time": round((end_time * 1000)),
                "game_version": find_eg_game_version(GAMEFOLDERNAME),
            }
    except Exception as e:
        logging.error("Something went wrong running the benchmark!")
        logging.exception(e)
        exit_code = 1
    finally:
        terminate_processes(PROCESS_NAME)
        am.create_manifest()
        if report is not None:
            write_report_json(LOG_DIRECTORY, "report.json", report)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
