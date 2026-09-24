"""UL Procyon Office Productivity test script"""

import logging
import subprocess
import sys
import time
from pathlib import Path

from procyon_office_utils import (
    find_procyon_versions,
    find_test_version,
    get_install_path,
    regex_find_score_in_xml,
)

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.artifacts import create_artifacts_manifest
from harness_utils.output_logging import setup_logging
from harness_utils.paths import harness_directories
from harness_utils.report import seconds_to_milliseconds, write_report_json

logger = logging.getLogger(__name__)

#####
# Globals
#####
SCRIPT_DIRECTORY, LOG_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)

DIR_PROCYON = Path(get_install_path())
EXECUTABLE = "ProcyonCmd.exe"
ABS_EXECUTABLE_PATH = DIR_PROCYON / EXECUTABLE
CONFIG_DIR = SCRIPT_DIRECTORY / "config"

CONFIG = CONFIG_DIR / "office_productivity.def"

RESULTS_FILENAME = "result.xml"
RESULTS_XML_PATH = ARTIFACTS_DIRECTORY / RESULTS_FILENAME
PROCYON_LOG_PATH = ARTIFACTS_DIRECTORY / "procyon_log.txt"

BENCHMARK_SCORES = {
    "Overall": r"<OfficeProductivityScore>(\d+)",
    "Word": r"<OfficeProductivityWordOverallScore>(\d+)",
    "Excel": r"<OfficeProductivityExcelOverallScore>(\d+)",
    "Powerpoint": r"<OfficeProductivityPowerpointOverallScore>(\d+)",
    "Outlook": r"<OfficeProductivityOutlookOverallScore>(\d+)",
}


def create_procyon_command():
    """Create Procyon command."""
    return [
        str(ABS_EXECUTABLE_PATH),
        f"--definition={CONFIG}",
        f"--export={RESULTS_XML_PATH}",
        f"--log={PROCYON_LOG_PATH}",
    ]


def run_benchmark(command_to_run):
    """Run the benchmark."""
    with subprocess.Popen(
        command_to_run,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as proc:
        logger.info("Procyon Office Productivity benchmark has started.")
        proc.communicate()
        
        return proc


try:
    setup_logging(LOG_DIRECTORY)

    test_version = find_test_version()
    cmd = create_procyon_command()
    logger.info("Starting benchmark!")
    logger.info(cmd)

    start_time = time.time()
    pr = run_benchmark(cmd)

    if pr.returncode > 0:
        logger.error("Procyon exited with return code %d", pr.returncode)
        sys.exit(pr.returncode)

    procyon_client_version, procyon_product_version = find_procyon_versions(
        PROCYON_LOG_PATH
    )

    if procyon_product_version is None:
        logger.warning("Could not determine Procyon Product Version.")

    if procyon_client_version is None:
        logger.warning("Could not determine Procyon Client Version.")

    logger.info("Procyon Client Version: %s", procyon_client_version)
    logger.info("Procyon Product Version: %s", procyon_product_version)

    end_time = time.time()
    elapsed_test_time = round(end_time - start_time, 2)

    logger.info("Benchmark took %.2f seconds", elapsed_test_time)

    session_report = []
    
    for score_name, score_regex in BENCHMARK_SCORES.items():
        score = regex_find_score_in_xml(score_regex)

        if score is None:
            logger.error("Could not find %s score!", score_name)
            sys.exit(1)

        logger.info("%s score was %s", score_name, score)

        report = {
            "start_time": seconds_to_milliseconds(start_time),
            "end_time": seconds_to_milliseconds(end_time),
            "test": "Procyon Office Benchmark",
            "test_parameter": score_name,
            "test_version": test_version,
            "procyon_client_version": procyon_client_version,
            "procyon_product_version": procyon_product_version,
            "unit": "score",
            "score": score,
        }

        session_report.append(report)

    write_report_json(LOG_DIRECTORY, "report.json", session_report)
    create_artifacts_manifest(ARTIFACTS_DIRECTORY)

except BaseException:
    logger.error("Something went wrong running the benchmark!")
    logger.exception("Unhandled exception")
    sys.exit(1)
