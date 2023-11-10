"""GravityMark test script"""
import logging
import getpass
import subprocess
import sys
from pathlib import Path
from gravitymark_utils import get_args, get_score, create_gravitymark_command

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    write_report_json
)

GRAVITYMARK_PATH = Path("C:/", "Program Files", "GravityMark", "bin")
GRAVITYMARK_EXE = GRAVITYMARK_PATH / "GravityMark.exe"

args = get_args()
api = f"-{args.api}"

script_dir = Path(__file__).resolve().parent
log_dir = script_dir / "run"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "harness.log"
logging.basicConfig(
    filename=log_file,
    format=DEFAULT_LOGGING_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    level=logging.DEBUG
)
console = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

gravitymark_log_path = Path("C:/Users", getpass.getuser(), ".GravityMark", "GravityMark.log")
image_path = log_dir / "result.png"
command = create_gravitymark_command(GRAVITYMARK_EXE, api, image_path)

try:
    logging.info('Starting benchmark!')
    # Remove existing log file so we have a fresh file with only the logs of the current run
    gravitymark_log_path.unlink(missing_ok=True)
    result = subprocess.run(command, check=True, cwd=GRAVITYMARK_PATH)

    if result.returncode > 0:
        logging.error("GravityMark exited with return code %d", result.returncode)
        sys.exit(1)

    score = get_score(gravitymark_log_path)

    if score is None:
        logging.error("Score not found")
        sys.exit(1)

    report = {
        "api": args.api,
        "score": score
    }

    write_report_json(log_dir, "report.json", report)
except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
