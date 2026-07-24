"""File cleanup helpers for harnesses."""

import logging
import os

logger = logging.getLogger(__name__)


def remove_files(paths: list[str]) -> None:
    """Remove provided file paths, ignoring paths that no longer exist."""
    for path in paths:
        try:
            os.remove(path)
            logger.debug("Removed file: %s", path)
        except FileNotFoundError:
            logger.debug("File already removed: %s", path)
