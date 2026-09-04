"""Strange Brigade Benchmark Script"""

import logging
import re
import shutil
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.file_cleanup import remove_files
from harness_utils.input import mangohud_log_toggle, press
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories, local_appdata
from harness_utils.platform import is_linux
from harness_utils.process import terminate_process
from harness_utils.report import (
    format_resolution,
    seconds_to_milliseconds,
    write_report_json,
)
from harness_utils.steam import exec_steam_game, get_app_install_location, get_build_id

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "StrangeBrigade.exe"
STEAM_GAME_ID = 312670
CAPTURE_PATH = SCRIPT_DIRECTORY / "capture"
CONFIG_LOCATION = local_appdata(STEAM_GAME_ID) / "Strange Brigade"
CONFIG_FILENAME = "GraphicsOptions.ini"
CONFIG_FULL_PATH = CONFIG_LOCATION / CONFIG_FILENAME
GAME_PATH = get_app_install_location(STEAM_GAME_ID)
EXE_PATH = GAME_PATH / "bin"
VIDEO_PATH = GAME_PATH / "FMV"

intro_videos = [VIDEO_PATH / "rebellion.webm"]


def read_current_resolution() -> tuple[int, int]:
    """Read the current resolution from the game config."""
    width_pattern = re.compile(r"Resolution_Width = (\d+);")
    height_pattern = re.compile(r"Resolution_Height = (\d+);")
    width = 0
    height = 0
    with CONFIG_FULL_PATH.open(encoding="utf-8") as file:
        for line in file:
            width_match = width_pattern.search(line)
            height_match = height_pattern.search(line)
            if width_match is not None:
                width = int(width_match.group(1))
            if height_match is not None:
                height = int(height_match.group(1))
    return width, height


def replace_exe(render_engine):
    """Replace the launcher with the selected renderer executable."""
    check_backup = EXE_PATH / "StrangeBrigade_launcher.exe"
    launcher_exe = EXE_PATH / "StrangeBrigade.exe"

    if render_engine == "vulkan":
        engine_exe = EXE_PATH / "StrangeBrigade_Vulkan.exe"
    elif render_engine == "dx12":
        engine_exe = EXE_PATH / "StrangeBrigade_DX12.exe"
    else:
        raise ValueError(f"Unsupported render engine: {render_engine}")

    staged_exe = EXE_PATH / "StrangeBrigade_harness.exe"
    shutil.copy(engine_exe, staged_exe)

    if not check_backup.exists():
        staged_backup = EXE_PATH / "StrangeBrigade_launcher_harness.exe"
        try:
            shutil.copy(launcher_exe, staged_backup)
        except OSError:
            staged_backup.unlink(missing_ok=True)
            raise
        staged_backup.replace(check_backup)

    staged_exe.replace(launcher_exe)
    logger.info("Launcher replaced with %s", engine_exe.name)


def restore_exe():
    """Restore the original launcher executable."""
    check_backup = EXE_PATH / "StrangeBrigade_launcher.exe"
    launcher_exe = EXE_PATH / "StrangeBrigade.exe"
    if not check_backup.exists():
        logger.info("No launcher backup found.")
        return

    check_backup.replace(launcher_exe)
    logger.info("Original launcher restored.")


def run_benchmark(render_engine):
    """Starts the benchmark"""
    logger.debug("deleting intro videos")
    remove_files([str(path) for path in intro_videos])
    replace_exe(render_engine)
    is_vulkan = False
    if render_engine == "vulkan":
        is_vulkan = True
    exec_steam_game(STEAM_GAME_ID)
    setup_start_time = int(time.time())
    time.sleep(30)

    result = find_word("options", timeout=120, vulkan=is_vulkan, interval=3)
    if not result:
        logger.info("Did not find the options menu. Did the game launch?")
        sys.exit(1)

    if is_linux():
        mangohud_log_toggle()

    press("down*5,left,enter")

    result = find_word("display", timeout=10, vulkan=is_vulkan)
    if not result:
        logger.info("Did not find the display menu. Did OCR navigate correctly?")
        sys.exit(1)

    press("pagedown")

    result = find_word("customise", timeout=10, vulkan=is_vulkan)
    if not result:
        logger.info(
            "Did not find the customize graphics detail option. Did navigate correctly?"
        )
        sys.exit(1)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "display.png", vulkan=is_vulkan)

    time.sleep(0.5)
    press("escape, down*5, enter")

    elapsed_setup_time = round(int(time.time()) - setup_start_time, 2)
    logger.info("Setup took %f seconds", elapsed_setup_time)
    time.sleep(1)
    result = find_word("strange", timeout=100, vulkan=is_vulkan)
    if not result:
        logger.info("Could not find FPS. Unable to mark start time!")
        sys.exit(1)

    test_start_time = int(time.time())

    time.sleep(55)  # Wait time for battle benchmark

    result = find_word("confirm", timeout=30, vulkan=is_vulkan)
    if not result:
        logger.info(
            "Results screen was not found! Did harness not wait long enough? Or test was too long?"
        )
        sys.exit(1)

    test_end_time = int(time.time()) - 1

    # Wait 5 seconds for benchmark info
    time.sleep(5)

    capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png", vulkan=is_vulkan)
    copy_artifact(CONFIG_FULL_PATH, ARTIFACTS_DIRECTORY)

    # End the run
    elapsed_test_time = round(test_end_time - test_start_time, 2)
    logger.info("Benchmark took %f seconds", elapsed_test_time)

    # Exit
    terminate_process(PROCESS_NAME)

    time.sleep(5)

    return test_start_time, test_end_time


def main():
    setup_logging(LOG_DIRECTORY)

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--render_engine",
        choices=["vulkan", "dx12"],
        help="Render Engine",
        required=True,
    )
    args, _ = parser.parse_known_args()

    try:
        start_time, endtime = run_benchmark(args.render_engine)
        height, width = read_current_resolution()
        report = {
            "resolution": format_resolution(width, height),
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(endtime),
            "version": get_build_id(STEAM_GAME_ID),
        }

        write_report_json(LOG_DIRECTORY, "report.json", report)
        create_artifacts_manifest(ARTIFACTS_DIRECTORY)
    except Exception:
        logger.error("Something went wrong running the benchmark!")
        logger.exception("Unhandled exception")
        terminate_process(PROCESS_NAME)
        sys.exit(1)
    finally:
        restore_exe()


if __name__ == "__main__":
    main()
