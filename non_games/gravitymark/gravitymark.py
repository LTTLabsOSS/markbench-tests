"""GravityMark test script"""

import logging
import subprocess
import sys
from pathlib import Path

from gravitymark_utils import (
    ASTEROID_COUNT,
    RESOLUTION_OPTION,
    create_gravitymark_command,
    ensure_gravitymark,
    friendly_test_param,
    get_args,
    get_gravitymark_log_path,
    get_score,
    validate_api,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import (
    copy_artifact,
    create_artifacts_manifest,
)
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import write_report_json

logger = logging.getLogger(__name__)



args = get_args()
validate_api(args.api)
API = f"-{args.api}"
RES = f"-mode {RESOLUTION_OPTION[args.resolution]}"
ASTEROIDS = f"-asteroids {ASTEROID_COUNT[args.asteroids]}"

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
setup_logging(LOG_DIRECTORY)

GRAVITYMARK_EXE, GRAVITYMARK_VERSION = ensure_gravitymark()
GRAVITYMARK_PATH = GRAVITYMARK_EXE.parent

GRAVITYMARK_LOG_PATH = get_gravitymark_log_path()
IMAGE_PATH = ARTIFACTS_DIRECTORY / "results.png"
command = create_gravitymark_command(GRAVITYMARK_EXE, API, ASTEROIDS, RES, IMAGE_PATH)

try:
    logger.info("Starting benchmark!")
    # Remove existing log file so we have a fresh file with only the logs of the current run
    GRAVITYMARK_LOG_PATH.unlink(missing_ok=True)
    result = subprocess.run(command, check=True, cwd=GRAVITYMARK_PATH)

    if result.returncode > 0:
        logger.error("GravityMark exited with return code %d", result.returncode)
        sys.exit(1)

    score = get_score(GRAVITYMARK_LOG_PATH)

    if score is None:
        logger.error("Score not found")
        sys.exit(1)

    copy_artifact(GRAVITYMARK_LOG_PATH, ARTIFACTS_DIRECTORY)
    report = {
        "test": "GravityMark",
        "test_parameter": (
        f"{friendly_test_param(args.api)} "
        f"{args.resolution}p "
        f"{args.asteroids.replace('mil', 'M').replace('k', 'K')}"
        ),
        "score": score,
        "unit": "score",
        "version": GRAVITYMARK_VERSION, 
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)
except Exception:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    sys.exit(1)
