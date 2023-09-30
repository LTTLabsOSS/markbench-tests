"""Misc utility functions"""
import logging
import os


def remove_files(paths: list[str]) -> None:
    """Removes files specified by provided list of file paths.
    Does nothing for a path that does not exist.
    """
    for path in paths:
        try:
            os.remove(path)
            logging.info("Removed file: %s", path)
        except FileNotFoundError:
            pass
