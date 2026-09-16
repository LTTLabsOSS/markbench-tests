"""Test script for primesieve"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)

sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.output_logging import setup_logging
from primesieve_utils import (
    PRIMESIEVE_VERSION,
    current_time_ms,
    ensure_primesieve,
    get_primesieve_version,
)

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"

setup_logging(LOG_DIRECTORY)

executable_path = ensure_primesieve()
command = str(executable_path).rstrip()

version = get_primesieve_version(command)

if version != PRIMESIEVE_VERSION:
    raise RuntimeError(
    f"PrimeSieve version {version} detected. "
    f"Version {PRIMESIEVE_VERSION} is required."
    )

logger.info(
    f"Starting PrimeSieve {version} benchmark"
    )

scores = []

start_time = current_time_ms()

for i in range(3):
    output = subprocess.check_output(
        [command, "1e12", "--quiet", "--time"],
        text=True,
    )

    score_pattern = r"Seconds:\s(\d+\.\d+)"

    if "Seconds" in output:
        duration = re.match(score_pattern, output).group(1)
        scores.append(float(duration))

end_time = current_time_ms()

SCORE_SUM = 0

for score in scores:
    SCORE_SUM += score

avg_score = round(SCORE_SUM / len(scores), 2)

report = {
    "start_time": start_time,
    "version": version,
    "end_time": end_time,
    "score": avg_score,
    "unit": "seconds",
    "test": "Primesieve 1e12",
}

with open(
    LOG_DIRECTORY / "report.json",
    "w",
    encoding="utf-8",
) as report_file:
    report_file.write(json.dumps(report))