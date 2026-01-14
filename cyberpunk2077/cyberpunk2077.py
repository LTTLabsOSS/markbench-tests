import sys
from pathlib import Path

HARNESSES_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(1, str(HARNESSES_ROOT))

from cyberpunk_run import run_benchmark
from cyberpunk_utils import copy_no_intro_mod, start_game, write_report

from harness_utils.artifacts import ArtifactManager
from harness_utils.helper import get_ocr_args
from harness_utils.output import setup_logging
from harness_utils.process import terminate_processes
from harness_utils.screenshot import Screenshotter

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "cyberpunk2077.exe"


setup_logging(LOG_DIRECTORY)

args = get_ocr_args()

sc = Screenshotter()
am = ArtifactManager(LOG_DIRECTORY, sc)

copy_no_intro_mod()
start_game()
start_time, end_time = run_benchmark(sc, am)
terminate_processes(PROCESS_NAME)
am.create_manifest()
sc.close()
write_report(LOG_DIRECTORY, start_time, end_time)
sys.exit(0)

