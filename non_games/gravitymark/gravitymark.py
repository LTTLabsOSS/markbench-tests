"""GravityMark test script"""

import getpass
import logging
import subprocess
import sys
from pathlib import Path

from gravitymark_utils import (
    create_gravitymark_command,
    friendly_test_param,
    get_args,
    get_score,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import write_report_json

logger = logging.getLogger(__name__)

GRAVITYMARK_PATH = Path("C:/", "Program Files", "GravityMark", "bin")
GRAVITYMARK_EXE = GRAVITYMARK_PATH / "GravityMark.exe"

args = get_args()
API = f"-{args.api}"

SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)
setup_logging(LOG_DIRECTORY)
ARTIFACTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

GRAVITYMARK_LOG_PATH = Path(
    "C:/Users", getpass.getuser(), ".GravityMark", "GravityMark.log"
)
IMAGE_PATH = ARTIFACTS_DIRECTORY / "results.png"
command = create_gravitymark_command(GRAVITYMARK_EXE, API, IMAGE_PATH)

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

    report = {
        "test": "GravityMark",
        "test_parameter": friendly_test_param(args.api),
        "score": score,
        "unit": "score",
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logger.error("Something went wrong running the benchmark!")
    logger.exception(e)
    sys.exit(1)
