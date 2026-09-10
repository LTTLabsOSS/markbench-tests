"""Utility harness for clicking the bottom-right corner using 4K coordinates."""

import logging
import sys
import time
from pathlib import Path

PARENT_DIRECTORY = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(1, PARENT_DIRECTORY)

from harness_utils.input import click
from harness_utils.output_logging import setup_logging

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
LOG_DIRECTORY = SCRIPT_DIRECTORY / "run"


def main() -> None:
    setup_logging(LOG_DIRECTORY)
    logger.info("Waiting 5 seconds before clicking the bottom-right corner")
    time.sleep(5)
    logger.info("Clicking at 4K coordinates (3839, 2159)")
    click(3839, 2159)
    logger.info("Click complete")


if __name__ == "__main__":
    main()
