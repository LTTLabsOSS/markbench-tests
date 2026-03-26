"""The Last of Us Part I test script."""

import logging
import os
import sys
import time
from pathlib import Path

from the_last_of_us_part_i_utils import copy_autosave, get_resolution

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import FAILED_RUN, find_word, press
from harness_utils.output import (
    format_resolution,
    seconds_to_milliseconds,
    setup_logging,
    write_report_json,
)
from harness_utils.process import terminate_processes
from harness_utils.steam import exec_steam_run_command, get_registry_active_user

STEAM_GAME_ID = 1888930
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "tlou"


def launch_game() -> None:
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(10)

    if not find_word("press", interval=3, timeout=60, msg="Did not see start screen"):
        return FAILED_RUN

    copy_autosave()
    time.sleep(5)
    press("space")

    if not find_word("options", interval=3, timeout=60, msg="Did not see main menu. Did something mess up?"):
        return FAILED_RUN
    press("s*2, enter")
    if not find_word("display", interval=3, timeout=60, msg="Did not see options menu (looking for display). Did something mess up?"):
        return FAILED_RUN
    press("s*4, enter")
    if not find_word("aspect", interval=3, timeout=60, msg="Did not see aspect ratio setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("01_video_1.png", ArtifactType.CONFIG_IMAGE)
    press("s*14")
    if not find_word("safezone", interval=3, timeout=60, msg="Did not see safezone scale setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("02_video_2.png", ArtifactType.CONFIG_IMAGE)
    press("s*7")
    if not find_word("gore", interval=3, timeout=60, msg="Did not see gore setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("03_video_3.png", ArtifactType.CONFIG_IMAGE)

    press("backspace")
    if not find_word("graphics", interval=3, timeout=60, msg="Did not see options menu (looking for graphics). Did something mess up?"):
        return FAILED_RUN
    press("s, enter")
    if not find_word("preset", interval=3, timeout=60, msg="Did not see graphics preset setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("04_graphics_1.png", ArtifactType.CONFIG_IMAGE)
    press("s*10")
    if not find_word("sampling", interval=3, timeout=60, msg="Did not see texture sampling quality setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("05_graphics_2.png", ArtifactType.CONFIG_IMAGE)
    press("s*7")
    if not find_word("point", interval=3, timeout=60, msg="Did not see point lights shadow resolution setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("06_graphics_3.png", ArtifactType.CONFIG_IMAGE)
    press("s*8")
    if not find_word("tracing", interval=3, timeout=60, msg="Did not see screen space cone tracing setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("07_graphics_4.png", ArtifactType.CONFIG_IMAGE)
    press("s*7")
    if not find_word("scattering", interval=3, timeout=60, msg="Did not see screen space sub-surface scattering setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("08_graphics_5.png", ArtifactType.CONFIG_IMAGE)
    press("s*6")
    if not find_word("bloom", interval=3, timeout=60, msg="Did not see bloom resolution setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("09_graphics_6.png", ArtifactType.CONFIG_IMAGE)
    press("s*6")
    if not find_word("ambient", interval=3, timeout=60, msg="Did not see ambient character density setting. Did something mess up?"):
        return FAILED_RUN
    am.take_screenshot("10_graphics_7.png", ArtifactType.CONFIG_IMAGE)

    press("backspace*2")
    if not find_word("behind", interval=3, timeout=60, msg="Did not see main menu after taking the graphics screenshots. Did something mess up?"):
        return FAILED_RUN

    press("w*2, space")
    if not find_word("load", interval=3, timeout=60, msg="Did not see story menu. Did something mess up?"):
        return FAILED_RUN
    press("s*2, space")
    if not find_word("hometown", interval=3, timeout=60, msg="Did not saves to load. Did something mess up? Or did you forget to delete the saves?"):
        return FAILED_RUN
    press("space")

    if not find_word("yes", timeout=10, interval=1, msg="Did not load the save"):
        return FAILED_RUN
    press("a, space")

    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))
    if not find_word("tommy", interval=0.2, timeout=250, msg="Did not see Tommy's first subtitle. Did the game load?"):
        return FAILED_RUN
    test_start_time = int(time.time())
    time.sleep(150)
    if not find_word("fromy", interval=0.2, timeout=250, msg="Did not find prompt to end harness."):
        return FAILED_RUN
    time.sleep(24)
    test_end_time = int(time.time())
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    logging.info("Sleeping to let steam cloud catch up as to avoid overriding.")
    time.sleep(10)
    return test_start_time, test_end_time


def main() -> None:
    """Run The Last of Us Part I benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            steam_id = get_registry_active_user()
            config_path = (
                Path(os.environ["USERPROFILE"])
                / "Saved Games"
                / "The Last of Us Part I"
                / "users"
                / str(steam_id)
                / "screeninfo.cfg"
            )
            height, width = get_resolution(str(config_path))
            report = {
                "resolution": format_resolution(width, height),
                "start_time": seconds_to_milliseconds(start_time),
                "end_time": seconds_to_milliseconds(end_time),
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
