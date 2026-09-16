"""Launch F1 24 and pause if OCR finds markbench."""

import logging
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.file_cleanup import remove_files
from harness_utils.ocr_service import find_word
from harness_utils.output_logging import setup_logging
from harness_utils.paths import game_install_path, harness_directories
from harness_utils.process import terminate_process
from harness_utils.report import seconds_to_milliseconds, write_report_json
from harness_utils.steam import exec_steam_game

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
PROCESS_NAME = "F1_24.exe"
STEAM_GAME_ID = 2488620

setup_logging(LOG_DIRECTORY)

try:
    video_path = game_install_path(STEAM_GAME_ID) / "videos"
    remove_files([str(video_path / "attract.bk2"), str(video_path / "cm_f1_sting.bk2")])
    exec_steam_game(STEAM_GAME_ID)
    start_time = time.time()
    time.sleep(20)

    if find_word("markbench", timeout=30, interval=1) is not None:
        logger.warning(
            "Found 'markbench'. Paused until the harness is manually stopped."
        )
        while True:
            time.sleep(1)

    end_time = time.time()
    report = {
        "start_time": seconds_to_milliseconds(start_time),
        "end_time": seconds_to_milliseconds(end_time),
    }
    write_report_json(LOG_DIRECTORY, "report.json", report)
    logger.info("No 'markbench' found. Run succeeded.")
except KeyboardInterrupt:
    logger.info("Harness stopped manually.")
    sys.exit(130)
except Exception:
    logger.exception("F1 24 launch test failed.")
    sys.exit(1)
finally:
    terminate_process(PROCESS_NAME)
