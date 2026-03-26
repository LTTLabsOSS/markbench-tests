"""Red Dead Redemption 2 test script."""

import getpass
import logging
import sys
import time
from pathlib import Path

from red_dead_redemption_2_utils import get_resolution

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
from harness_utils.steam import exec_steam_run_command, get_build_id

STEAM_GAME_ID = 1174180
PROCESS_NAME = "RDR2"
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
CONFIG_FULL_PATH = Path(
    "C:/Users/",
    getpass.getuser(),
    "Documents",
    "Rockstar Games",
    "Red Dead Redemption 2",
    "Settings",
    "system.xml",
)


def launch_game() -> None:
    exec_steam_run_command(STEAM_GAME_ID)


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Start the benchmark."""
    launch_game()
    setup_start_time = int(time.time())
    time.sleep(80)

    if find_word("strange", vulkan=True, timeout=30, interval=1):
        press("enter")
        time.sleep(3)

    if not find_word("settings", vulkan=True, timeout=30, interval=1, msg="Did not find the settings menu. Did the game launch?"):
        return FAILED_RUN
    press("z")
    time.sleep(3)

    if not find_word("graphics", vulkan=True, timeout=5, interval=1, msg="Did not find the graphics menu. Did keras get stuck?"):
        return FAILED_RUN
    press("up*2, left*2, down, enter")
    time.sleep(3)

    if not find_word("resolution", vulkan=True, timeout=5, interval=1, msg="Did not find the resolution setting. Did the game navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("01_graphics_1.png", ArtifactType.CONFIG_IMAGE)

    if find_word("nvidia", vulkan=True, timeout=5, interval=1):
        logging.info("NVIDIA card is installed, navigating accordingly.")
        press("down*26")
        if not find_word("mode", vulkan=True, timeout=5, interval=1, msg="Did not find the FSR mode description. Did it navigate correctly?"):
            return FAILED_RUN
        am.take_screenshot_vulkan("02_graphics_2.png", ArtifactType.CONFIG_IMAGE)
        press("down*14")
        if not find_word("long", vulkan=True, timeout=5, interval=1, msg="Did not find the Long Shadows settings. Did it navigate correctly?"):
            return FAILED_RUN
        am.take_screenshot_vulkan("03_graphics_3.png", ArtifactType.CONFIG_IMAGE)
        press("down*15")
    else:
        logging.info("NVIDIA card not detected on screen, navigating accordingly.")
        press("down*26")
        if not find_word("msaa", vulkan=True, timeout=5, interval=1, msg="Did not find the MSAA settings. Did Keras navigate correctly?"):
            return FAILED_RUN
        am.take_screenshot_vulkan("02_graphics_2.png", ArtifactType.CONFIG_IMAGE)
        press("down*14")
        if not find_word("reflection", vulkan=True, timeout=5, interval=1, msg="Did not find the Water Reflection Quality settings. Did Keras navigate correctly?"):
            return FAILED_RUN
        am.take_screenshot_vulkan("03_graphics_3.png", ArtifactType.CONFIG_IMAGE)
        press("down*12")

    if not find_word("tessellation", vulkan=True, timeout=5, interval=1, msg="Did not find the Tree Tessellation settings. Did Keras navigate correctly?"):
        return FAILED_RUN
    am.take_screenshot_vulkan("04_graphics_4.png", ArtifactType.CONFIG_IMAGE)

    if not find_word("benchmark", vulkan=True, timeout=5, interval=1, msg="Did not see the Run Benchmark Test at the bottom of the screen. Did navigation mess up?"):
        return FAILED_RUN

    import pydirectinput as user  # localize legacy hold-key behavior

    user.keyDown("x")
    time.sleep(1.5)
    user.keyUp("x")
    logging.info("Setup took %f seconds", round(int(time.time()) - setup_start_time, 2))
    press("enter")

    if not find_word("stop", vulkan=True, timeout=60, interval=1, msg="Did not find the stop benchmarking in the corner. Did the benchmark crash?"):
        return FAILED_RUN
    test_start_time = int(time.time())

    time.sleep(270)
    if not find_word("end", vulkan=True, timeout=30, interval=1, msg="Did not find the end results screen. Did the benchmark crash?"):
        return FAILED_RUN

    test_end_time = int(time.time())
    am.take_screenshot_vulkan("05_results.png", ArtifactType.RESULTS_IMAGE)
    am.copy_file(Path(CONFIG_FULL_PATH), ArtifactType.RESULTS_TEXT, "system.xml")
    logging.info("Benchmark took %f seconds", round(test_end_time - test_start_time, 2))
    time.sleep(50)
    return test_start_time, test_end_time


def main() -> None:
    """Run the Red Dead Redemption 2 benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            width, height = get_resolution()
            report = {
                "resolution": format_resolution(width, height),
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
