"""File helpers for harnesses."""

import logging
import os
import shutil
from pathlib import Path


def copy_to_directory(
    source: str | os.PathLike, destination: str | os.PathLike
) -> Path:
    """Copy a file into a directory while preserving its basename."""
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.mkdir(parents=True, exist_ok=True)
    output_path = destination_path / source_path.name
    try:
        shutil.copy(source_path, output_path)
    except OSError:
        logging.exception("Failed to copy %s to %s", source_path, output_path)
        raise
    return output_path


def remove_files(paths: list[str]) -> None:
    """Remove provided file paths, ignoring paths that no longer exist."""
    for path in paths:
        try:
            os.remove(path)
            logging.info("Removed file: %s", path)
        except FileNotFoundError:
            logging.info("File already removed: %s", path)


def reset_directory(path: str | os.PathLike) -> Path:
    """Replace a directory with an empty directory."""
    directory = Path(path)
    if directory.exists():
        try:
            shutil.rmtree(directory)
        except OSError:
            logging.exception("Failed to reset directory: %s", directory)
            raise
    directory.mkdir(parents=True, exist_ok=True)
    return directory
