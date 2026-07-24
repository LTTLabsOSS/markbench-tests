"""File cleanup helpers for harnesses."""

import logging
import os


def remove_files(paths: list[str]) -> None:
    """Remove provided file paths, ignoring paths that no longer exist."""
    for path in paths:
        try:
            os.remove(path)
            logging.debug("Removed file: %s", path)
        except FileNotFoundError:
            logging.debug("File already removed: %s", path)
