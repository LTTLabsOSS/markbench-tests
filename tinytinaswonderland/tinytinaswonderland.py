"""Tiny Tina's Wonderlands test script."""

import logging
import sys
import time
from pathlib import Path

from tinytinaswonderland_utils import (
    find_latest_result_file,
    get_documents_path,
    read_resolution,
)

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
from harness_utils.steam import exec_steam_game, get_build_id

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
STEAM_GAME_ID = 1286680
PROCESS_NAME = "Wonderlands"


def launch_game() -> None:
    exec_steam_game(STEAM_GAME_ID, game_params=["-nostartupmovies"])


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    """Run benchmark."""
    launch_game()
    setup_start_time = int(time.time())

    if find_word("optimize", interval=1, timeout=10):
        time.sleep(40)

    time.sleep(20)

    if not find_word("options", interval=1, timeout=60, msg="game did not load within time"):
        return FAILED_RUN

    logging.info("Saw the options! we are good to go!")
    press("down*2, enter")
    time.sleep(4)

    if not find_word("visuals", interval=1, timeout=10, msg="on the wrong menu!"):
        return FAILED_RUN

    am.take_screenshot("01_graphics_1.png", ArtifactType.CONFIG_IMAGE)
    press("altleft")
    am.take_screenshot("02_graphics_2.png", ArtifactType.CONFIG_IMAGE)
    time.sleep(1)
    press("down*18")
    am.take_screenshot("03_graphics_3.png", ArtifactType.CONFIG_IMAGE)
    press("altleft")

    if not find_word("benchmark", interval=1, timeout=10, msg="could not find benchmark button"):
        return FAILED_RUN

    press("down, enter")
    time.sleep(1)
    logging.info("Harness setup took %d seconds", round((int(time.time()) - setup_start_time), 2))

    if not find_word("fps", interval=0.5, timeout=30, msg="benchmark didn't start on time or at all"):
        return FAILED_RUN

    benchmark_start = int(time.time())
    time.sleep(110)

    if not find_word(
        "options",
        interval=0.5,
        timeout=30,
        msg="did not detect end of benchmark, should have landed back in main menu",
    ):
        return FAILED_RUN

    benchmark_end = int(time.time())
    logging.info("Benchmark took %d seconds", round((benchmark_end - benchmark_start), 2))

    my_documents_path = get_documents_path()
    settings_path = Path(
        my_documents_path,
        r"My Games\Tiny Tina's Wonderlands\Saved\Config\WindowsNoEditor\GameUserSettings.ini",
    )
    am.copy_file(settings_path, ArtifactType.CONFIG_TEXT, "settings file")
    saved_results_dir = Path(
        my_documents_path, r"My Games\Tiny Tina's Wonderlands\Saved\BenchmarkData"
    )
    benchmark_results = find_latest_result_file(str(saved_results_dir))
    am.copy_file(benchmark_results, ArtifactType.RESULTS_TEXT, "results file")
    return benchmark_start, benchmark_end


def main() -> None:
    """Run the Tiny Tina's Wonderlands benchmark harness."""
    setup_logging(LOG_DIRECTORY)
    am = ArtifactManager(LOG_DIRECTORY)
    report = None
    exit_code = 0

    try:
        start_time, end_time = run_benchmark(am)
        if (start_time, end_time) == FAILED_RUN:
            exit_code = 1
        else:
            height, width = read_resolution()
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
