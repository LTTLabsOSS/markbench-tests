"""GravityMark test script"""
import logging
import getpass
import subprocess
import sys
from pathlib import Path
from gravitymark_utils import friendly_test_param, get_args, get_score, create_gravitymark_command

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output import (
    setup_logging,
    write_report_json)

GRAVITYMARK_PATH = Path("C:/", "Program Files", "GravityMark", "bin")
GRAVITYMARK_EXE = GRAVITYMARK_PATH / "GravityMark.exe"

args = get_args()
API = f"-{args.api}"

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
setup_logging(LOG_DIRECTORY)

GRAVITYMARK_LOG_PATH = Path(
    "C:/Users", getpass.getuser(),
    ".GravityMark", "GravityMark.log")
IMAGE_PATH = LOG_DIRECTORY / "result.png"
command = create_gravitymark_command(GRAVITYMARK_EXE, API, IMAGE_PATH)

try:
    logging.info('Starting benchmark!')
    # Remove existing log file so we have a fresh file with only the logs of the current run
    GRAVITYMARK_LOG_PATH.unlink(missing_ok=True)
    result = subprocess.run(command, check=True, cwd=GRAVITYMARK_PATH)

    if result.returncode > 0:
        logging.error("GravityMark exited with return code %d",
                      result.returncode)
        sys.exit(1)

    score = get_score(GRAVITYMARK_LOG_PATH)

    if score is None:
        logging.error("Score not found")
        sys.exit(1)

    report = {
        "test": "GravityMark",
        "test_parameter": friendly_test_param(args.api),
        "score": score,
        "unit": "score"
    }

    write_report_json(LOG_DIRECTORY, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
