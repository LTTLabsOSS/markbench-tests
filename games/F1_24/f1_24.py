import logging
import sys
import time
from pathlib import Path

from f1_24_utils import find_latest_result_file, remove_intro_videos, write_report

HARNESS_UTILS_PARENT = Path(__file__).resolve().parents[2]
sys.path.insert(1, str(HARNESS_UTILS_PARENT))

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, int_time, press, terminate_process
from harness_utils.output import setup_logging

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "F1_24"

f1_folder = Path.home() / "Documents" / "My Games" / "F1 24"
CONFIG_PATH = f1_folder / "hardwaresettings"
CONFIG = CONFIG_PATH / "hardware_settings_config.xml"
BENCHMARK_RESULTS_PATH = f1_folder / "benchmark"


def startup() -> bool:
    if not find_word("product", timeout=60):
        return False

    press("space*3", pause=1)

    if not find_word("press", timeout=30):
        return False

    press("enter")

    if not find_word("login", timeout=30):
        return False

    press("enter")

    if not find_word("signed", timeout=30):
        return False

    press("enter")

    if not find_word("theatre", "Did not find theatre on main menu", timeout=60):
        return False

    return True


def settings_and_start(am: ArtifactManager) -> bool:
    press("down*6,enter")

    if not find_word("graphics"):
        return False

    press("right, enter")

    # check if in graphics here

    press("down*3,enter")

    if not find_word("vsync", "vsync in video menu not found"):
        return False

    # video fits on one page, may be necessary to scroll if smaller resolution

    am.take_screenshot("1_video.png", ArtifactType.CONFIG_IMAGE, "video setting")

    press("esc")

    if not find_word("steering", "sterring not found after leaving video menue"):
        return False

    am.take_screenshot(
        "2_graphics1.png", ArtifactType.CONFIG_IMAGE, "graphics settings 1"
    )
    press("down*29")

    if not find_word("chromatic"):
        return False

    am.take_screenshot(
        "3_graphics2.png", ArtifactType.CONFIG_IMAGE, "graphics settings2 "
    )

    press("up*28,enter")

    if not find_word("weather"):
        return False

    am.take_screenshot(
        "4_benchmark.png", ArtifactType.CONFIG_IMAGE, "benchmark settings"
    )

    press("down*6,enter")

    return True


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    # navigating settings

    if not startup():
        return (0, 0)

    if not settings_and_start(am):
        return (0, 0)

    # looking for start in time of benchmark
    if not find_word("lap", "lap at benchmark start not seen"):
        return (0, 0)

    test_start_time = int_time() + 8

    time.sleep(310)

    test_end_time = None

    if not find_word("loading", "loading screen not found"):
        return (0, 0)

    test_end_time = int_time() - 2
    time.sleep(2)

    if not find_word("results"):
        return (0, 0)

    am.take_screenshot(
        "result.png", ArtifactType.RESULTS_IMAGE, "screenshot of results"
    )

    return test_start_time, test_end_time


def main():
    setup_logging(LOG_DIRECTORY)

    am = ArtifactManager(LOG_DIRECTORY)

    remove_intro_videos()

    start_time, end_time = run_benchmark(am)

    terminate_process(PROCESS_NAME)

    if start_time and end_time == 0:
        logging.error("Benchmark Failed")
        sys.exit(1)

    results_file = find_latest_result_file(BENCHMARK_RESULTS_PATH)

    am.copy_file(CONFIG, ArtifactType.CONFIG_TEXT, "config file")

    am.copy_file(results_file, ArtifactType.RESULTS_TEXT, "benchmark results xml file")

    am.create_manifest()

    write_report(LOG_DIRECTORY, start_time, end_time)

    sys.exit(0)


if __name__ == "__main__":
    main()
