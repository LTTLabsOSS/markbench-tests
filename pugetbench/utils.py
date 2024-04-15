import re
import os
from pathlib import Path


def find_latest_log():
    appdata_path = os.getenv('LOCALAPPDATA')
    puget_lunch_dir = Path(appdata_path) / "com.puget.benchmark" / "csv"
    files = [os.path.join(puget_lunch_dir, file) for file in os.listdir(
        puget_lunch_dir) if os.path.isfile(os.path.join(puget_lunch_dir, file))]
    latest_file = max(files, key=os.path.getmtime)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return Path(script_dir) / latest_file


def find_score_in_log(log_path):
    with open(log_path, 'r') as file:
        for line in file:
            score = is_score_line(line)
            if score is not None:
                return score


def is_score_line(line):
    regex_pattern = r"^Overall Score.+,+(\d+),+"
    match = re.search(regex_pattern, line)
    if match and len(match.groups()) > 0:
        return match.group(1)
    else:
        return None
