"""utils file for pugetbench harness"""
import re
import os
from pathlib import Path
import win32api


def get_latest_benchmark_by_version(benchmark_name: str):
    """get latest benchmark version for photoshop or premiere"""
    valid_names = ['photoshop', 'premierepro']
    if benchmark_name not in valid_names:
        raise ValueError("invalid benchmark name")

    benchmark_json_dir = Path().home() / "AppData/Local/com.puget.benchmark/benchmarks"
    if not benchmark_json_dir.exists():
        raise ValueError("could not find benchmark directory in appdata")

    benchmark_files = [f for f in os.listdir(benchmark_json_dir) if benchmark_name in f]
    # sort assuming the filename format is still premierepro-benchmark-X.X.X.json
    # convert version to int and order by size
    sorted_files = sorted(benchmark_files, key=lambda x: tuple(map(int,x.split("-")[-1].split(".")[:-1])))
    latest_version = sorted_files[len(sorted_files)-1]
    latest_version = latest_version.split("-")[2]
    version, _ = latest_version.rsplit(".", 1)
    return version


def find_latest_log():
    """find latest log from pugetbench"""
    appdata_path = os.getenv('LOCALAPPDATA')
    puget_lunch_dir = Path(appdata_path) / "com.puget.benchmark" / "csv"
    files = [os.path.join(puget_lunch_dir, file) for file in os.listdir(
        puget_lunch_dir) if os.path.isfile(os.path.join(puget_lunch_dir, file))]
    latest_file = max(files, key=os.path.getmtime)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return Path(script_dir) / latest_file


def find_score_in_log(log_path):
    """find score in pugetbench log file"""
    with open(log_path, 'r', encoding="utf-8") as file:
        for line in file:
            score = is_score_line(line)
            if score is not None:
                return score
    return None


def is_score_line(line):
    """check if string is a score using regex"""
    regex_pattern = r"^Overall Score.+,+(\d+),+"
    match = re.search(regex_pattern, line)
    if match and len(match.groups()) > 0:
        return match.group(1)
    return None


def get_photoshop_version() -> str:
    """get current photoshop version string"""
    path = "C:\\Program Files\\Adobe\\Adobe Photoshop 2024\\Photoshop.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(path, str_info_path)
    except Exception as e:
        print(e)
    return None


def get_premierepro_version() -> str:
    """get current premiere pro version string"""
    path = "C:\\Program Files\\Adobe\\Adobe Premiere Pro 2024\\Adobe Premiere Pro.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(path, str_info_path)
    except Exception as e:
        print(e)
    return None
