"""Misc utility functions"""
import logging
import os
from pathlib import Path
from zipfile import ZipFile

import requests

def remove_files(paths: list[str]) -> None:
    """Removes files specified by provided list of file paths.
    Does nothing for a path that does not exist.
    """
    for path in paths:
        try:
            os.remove(path)
            logging.info("Removed file: %s", path)
        except FileNotFoundError:
            logging.info("File already removed: %s", path)


def download_file(download_url: str, destination: Path) -> None:
    """Downloads file from given url to destination"""
    response = requests.get(download_url, allow_redirects=True, timeout=120)
    with open(destination, 'wb') as f:
        f.write(response.content)


def extract_archive(zip_file: Path, destination_dir: Path) -> None:
    """Extract all contents of an archive"""
    with ZipFile(zip_file, 'r') as zip_object:
        zip_object.extractall(path=destination_dir)


def extract_file_from_archive(zip_file: Path, member_path: str, destination_dir: Path) -> None:
    """Extract a single file memeber from an archive"""
    with ZipFile(zip_file, 'r') as zip_object:
        zip_object.extract(member_path, path=destination_dir)