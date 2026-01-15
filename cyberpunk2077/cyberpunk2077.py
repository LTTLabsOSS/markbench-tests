import sys
from pathlib import Path

HARNESSES_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(1, str(HARNESSES_ROOT))

from cyberpunk_run import run_benchmark
from cyberpunk_utils import copy_no_intro_mod, start_game, write_report

from harness_utils.artifacts import ArtifactManager
from harness_utils.output import setup_logging
from harness_utils.process import terminate_processes

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"
PROCESS_NAME = "cyberpunk2077.exe"


setup_logging(LOG_DIRECTORY)

am = ArtifactManager(LOG_DIRECTORY)

copy_no_intro_mod()
start_game()
start_time, end_time = run_benchmark(am)
terminate_processes(PROCESS_NAME)
am.create_manifest()
write_report(LOG_DIRECTORY, start_time, end_time)
sys.exit(0)

