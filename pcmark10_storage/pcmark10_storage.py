"""UL PCMark 10 Storage test script"""

# pylint: disable=no-name-in-module
import logging
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

import psutil
from utils import (
    find_pcmark10_version,
    find_test_version,
    get_install_path,
    is_process_running,
    regex_find_score_in_xml,
)

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.output import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LOGGING_FORMAT,
    seconds_to_milliseconds,
    setup_log_directory,
    write_report_json,
)

#####
# Globals
#####
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "run"
DIR_PCMARK10 = Path(get_install_path())
EXECUTABLE = "PCMark10Cmd.exe"
ABS_EXECUTABLE_PATH = DIR_PCMARK10 / EXECUTABLE
CONFIG_DIR = SCRIPT_DIR / "config"
BENCHMARK_CONFIG = {
    "full": {
        "config": str(CONFIG_DIR / "pcm10_storage_full_default.pcmdef"),
        "process_name": "PCMark10-Storage.exe",
        "result_regex": r"<Pcm10StorageFullScore>(\d+)",
        "test_name": "full",
    },
    "quick": {
        "config": str(CONFIG_DIR / "pcm10_storage_quick_default.pcmdef"),
        "process_name": "PCMark10-Storage.exe",
        "result_regex": r"<Pcm10StorageQuickScore>(\d+)",
        "test_name": "quick",
    },
}

RESULTS_FILENAME = "result.xml"
RESULTS_XML_PATH = LOG_DIR / RESULTS_FILENAME


def setup_logging():
    """setup logging"""
    setup_log_directory(str(LOG_DIR))
    logging.basicConfig(
        filename=LOG_DIR / "harness.log",
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)


def get_arguments():
    """get arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "--drive_letter",
        default="C",  # <- default drive letter
        help="Drive letter to test (e.g. D). Defaults to C if not specified.",
    )
    parser.add_argument(
        "--test",
        dest="test",
        help="Test type",
        required=True,
        choices=BENCHMARK_CONFIG.keys(),
    )
    argies = parser.parse_args()
    return argies

def normalize_drive_letter(drive_letter: str) -> str:
    drive_letter = drive_letter.strip().upper()

    if len(drive_letter) == 1:
        drive_letter += ":"

    if not drive_letter.endswith(":"):
        raise ValueError(f"Invalid drive letter: {drive_letter}")

    return drive_letter

def create_pcmark10_command(drive_letter, test_option):
    """create command string"""
    command = [
            str(ABS_EXECUTABLE_PATH),
            f"--drive={drive_letter}",
            f"--definition={test_option}",
            f"--export={RESULTS_XML_PATH}"
    ]
    return command


def run_benchmark(process_name, command_to_run, start_time):
    """run the benchmark"""
    with subprocess.Popen(
        command_to_run,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as proc:
        logging.info("PCMark 10 Storage benchmark has started.")
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= 60:  # seconds
                raise ValueError("BenchMark subprocess did not start in time")
            process = is_process_running(process_name)
            if process is not None:
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                break
            time.sleep(0.2)
        _, _ = proc.communicate()  # blocks until 3dmark exits
        return proc


try:
    setup_logging()
    args = get_arguments()
    letter = normalize_drive_letter(args.drive_letter)
    option = BENCHMARK_CONFIG[args.test]["config"]
    cmd = create_pcmark10_command(letter,option)
    logging.info("Starting benchmark!")
    logging.info(cmd)
    start_time = time.time()
    pr = run_benchmark(BENCHMARK_CONFIG[args.test]["process_name"], cmd, start_time)

    if pr.returncode > 0:
        logging.error("PCMark 10 exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)

    am = ArtifactManager(LOG_DIR)
    am.copy_file(RESULTS_XML_PATH, ArtifactType.RESULTS_TEXT, "results xml file")
    am.create_manifest()
    results_regex = BENCHMARK_CONFIG[args.test]["result_regex"]
    score_str = regex_find_score_in_xml(results_regex)
    if not score_str:
        logging.error("Could not find overall score!")
        sys.exit(1)
    score = int(score_str)

    pcmark_version = find_pcmark10_version()
    if not pcmark_version:
        logging.error("Could not determine PCMark 10 version!")
        sys.exit(1)

    test_version = find_test_version()
    if not test_version:
        logging.error("Could not determine PCMark 10 test version!")
        sys.exit(1)

    report = {
            "test": "PCMark 10 Storage",
            "test_parameter": BENCHMARK_CONFIG[args.test]["test_name"],
            "unit": "score",
            "score": score,
            "pcmark10_version": pcmark_version,
            "test_version": test_version,
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
        }

    logging.info("Benchmark took %.2f seconds", elapsed_test_time)
    logging.info("Score was %s", score)

    write_report_json(str(LOG_DIR), "report.json", report)

except Exception as e:
    logging.error("Something went wrong running the benchmark!")
    logging.exception(e)
    sys.exit(1)
