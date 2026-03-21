import logging
import sys
import time
from pathlib import Path

import pydirectinput as user
from cyberpunk_utils import copy_no_intro_mod, read_current_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, press
from harness_utils.output import (
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_game, get_build_id

STEAM_GAME_ID = 1091500
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "cyberpunk2077.exe"
FAILED_RUN = (0, 0)

user.FAILSAFE = False


def launch_game():
    return exec_steam_game(
        STEAM_GAME_ID, game_params=["--launcher-skip", "-skipStartScreen"]
    )


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark"""
    copy_no_intro_mod()

    launch_game()

    time.sleep(20)

    if not find_word("new", timeout=60, msg="did not see 'new' on home screen"):
        return FAILED_RUN

    if not find_word("continue"):
        press("left, enter")
    else:
        press("left, down, enter")

    if not find_word("volume", msg="did not see 'volume' on settings screen"):
        return FAILED_RUN

    press("3*3")

    if not find_word(
        "preset",
        msg="did not see 'preset' on graphics settings screen",
    ):
        return FAILED_RUN

    am.take_screenshot("02_graphics_presets.png", ArtifactType.CONFIG_IMAGE)

    while not find_word("vignette", timeout=0):
        press("down")

    am.take_screenshot("03_graphics_basic.png", ArtifactType.CONFIG_IMAGE)

    press("down*11")

    if not find_word("decals", msg="did not see decals in advanced settings"):
        return FAILED_RUN

    am.take_screenshot("04_graphics_advanced1.png", ArtifactType.CONFIG_IMAGE)

    press("down*6")

    if not find_word("level", msg="did not see level in advanced settings"):
        return FAILED_RUN

    am.take_screenshot("05_graphics_advanced2.png", ArtifactType.CONFIG_IMAGE)

    press("3")

    if not find_word("resolution", interval=3, timeout=20):
        return FAILED_RUN
    am.take_screenshot("01_video.png", ArtifactType.CONFIG_IMAGE)

    press("b, enter")

    if not find_word("fps", timeout=60):
        return FAILED_RUN

    test_start_time = int(time.time()) - 5

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    time.sleep(60)
    if not find_word("results", timeout=60, interval=1):
        return FAILED_RUN

    am.take_screenshot("07_results.png", ArtifactType.RESULTS_IMAGE)

    test_end_time = int(time.time()) - 2
    time.sleep(2)

    return test_start_time, test_end_time


def main() -> None:
    """Run the Cyberpunk 2077 benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            resolution = read_current_resolution()
            report = {
                "resolution": f"{resolution}",
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
                "version": get_build_id(STEAM_GAME_ID),
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
