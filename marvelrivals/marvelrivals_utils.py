"""Marvel Rivals test script utils"""
import re
import sys
from pathlib import Path
import os

PARENT_DIR = str(Path(sys.path[0], ".."))
sys.path.append(PARENT_DIR)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
APPDATA = os.getenv("LOCALAPPDATA")
CONFIG_LOCATION = f"{APPDATA}\\Marvel\\Saved\\Config\\Windows"
CONFIG_FILENAME = "GameUserSettings.ini"


def read_resolution():
    """Gets resolution width and height values from local file"""
    height_pattern = re.compile(r"ResolutionSizeY=(\d+)")
    width_pattern = re.compile(r"ResolutionSizeX=(\d+)")
    cfg = f"{CONFIG_LOCATION}\\{CONFIG_FILENAME}"
    height = 0
    width = 0
    with open(cfg, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (height, width)

def find_latest_benchmarkcsv():
    """find latest log from the benchmark"""
    appdata_path = os.getenv('LOCALAPPDATA')
    benchmarkcsv_dir = Path(appdata_path) / "Marvel" / "Saved" / "Benchmark"
    files = [os.path.join(benchmarkcsv_dir, file) for file in os.listdir(
        benchmarkcsv_dir) if os.path.isfile(os.path.join(benchmarkcsv_dir, file))]
    latest_file = max(files, key=os.path.getmtime)
    return latest_file