"""Utility functions for Rainbow Six Siege X test script"""
import os
from pathlib import Path
import configparser
import winreg

USERPROFILE = os.getenv("USERPROFILE")
LOCALAPPDATA = os.getenv("LOCALAPPDATA")
USERNAME = os.getlogin()

def get_active_ubisoft_user_id():
    """
    Returns the most recently active Ubisoft Connect account ID by
    checking the cache/settings folder inside the launcher installation path.
    """


    settings_path = os.path.join(LOCALAPPDATA, "Ubisoft Game Launcher", "cache", "settings")
    if not os.path.exists(settings_path):
        return None

    candidates = []
    for entry in os.listdir(settings_path):
        full_path = os.path.join(settings_path, entry)
        if os.path.isdir(full_path) or os.path.isfile(full_path):
            mtime = os.path.getmtime(full_path)
            candidates.append((mtime, entry))

    if not candidates:
        return None

    # Sort by last modified (newest first)
    candidates.sort(reverse=True)
    return candidates[0][1]

def get_r6s_config_path():
    """
    Returns the full path to the active user's Rainbow Six Siege GameSettings.ini file,
    or None if not found.
    """
    active_user_id = get_active_ubisoft_user_id()
    if not active_user_id:
        return None

    ini_path = os.path.expandvars(
        rf"{USERPROFILE}\Documents\My Games\Rainbow Six - Siege\{active_user_id}\GameSettings.ini"
    )
    return ini_path if os.path.exists(ini_path) else None


def read_current_resolution():
    """
    Returns the active R6S resolution as a string formatted 'WIDTHxHEIGHT',
    or None if not available.
    """
    ini_path = get_r6s_config_path()
    if not ini_path:
        return None

    config = configparser.ConfigParser()
    config.optionxform = str  # preserve key case
    config.read(ini_path)

    try:
        width = config.getint("DISPLAY_SETTINGS", "ResolutionWidth")
        height = config.getint("DISPLAY_SETTINGS", "ResolutionHeight")
        return width, height
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return None

def find_latest_result_file():
    """Look for files in the benchmark results path that match the pattern.
    Returns the most recent benchmark file."""
    benchmark_results_path = Path(f"C:\\Users\\{USERNAME}\\Documents\\My Games\\Rainbow Six - Siege\\Benchmark")

    if not benchmark_results_path.exists():
        raise FileNotFoundError(f"Benchmark folder does not exist: {benchmark_results_path}")

    files = list(benchmark_results_path.glob("benchmark-*.html"))
    if not files:
        raise FileNotFoundError(f"No benchmark-*.html files found in {benchmark_results_path}")

    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)