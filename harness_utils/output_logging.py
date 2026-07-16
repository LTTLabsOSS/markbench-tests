"""Output logging setup helpers for harnesses."""

import logging
from pathlib import Path

DEFAULT_LOGGING_FORMAT = "[%(levelname)s] (%(asctime)s) %(message)s"
DEFAULT_DATE_FORMAT = "%H:%M:%S"


def setup_log_directory(log_dir: str | Path) -> None:
    """Create the log directory if it does not already exist."""
    Path(log_dir).mkdir(exist_ok=True)


def setup_logging(log_directory: str | Path) -> None:
    """Set up file and console logging for a harness."""
    setup_log_directory(log_directory)
    log_file = Path(log_directory) / "harness.log"

    logging.basicConfig(
        filename=log_file,
        format=DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    formatter = logging.Formatter(
        DEFAULT_LOGGING_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
