"""utils file for pugetbench harness"""
import re
import os
from pathlib import Path
import win32api


def get_latest_benchmark_by_version(benchmark_name: str):
    """Get the latest benchmark version, prioritizing beta if it's newer."""
    valid_names = ['photoshop', 'premierepro', 'aftereffects', 'resolve']
    if benchmark_name not in valid_names:
        raise ValueError("Invalid benchmark name")

    benchmark_json_dir = Path().home() / "AppData/Local/com.puget.benchmark/benchmarks"
    if not benchmark_json_dir.exists():
        raise ValueError("Could not find benchmark directory in appdata")

    # Find relevant benchmark files
    benchmark_files = [f for f in os.listdir(benchmark_json_dir) if f.startswith(f"{benchmark_name}-benchmark-")]

    if not benchmark_files:
        raise ValueError("No valid benchmark versions found.")

    version_pattern = re.compile(r'-(\d+)\.(\d+)\.(\d+)(-beta)?\.json$')

    def extract_version(filename):
        """Extracts numeric version and beta flag from filename."""
        match = version_pattern.search(filename)
        if match:
            major, minor, patch, beta_flag = match.groups()
            version = f"{major}.{minor}.{patch}"
            if beta_flag:
                version += "-beta"
            return version
        return None  # Ignore files that don't match

    # Extract valid versions
    versions = [extract_version(f) for f in benchmark_files]
    versions = [v for v in versions if v is not None]  # Filter out invalid matches

    if not versions:
        raise ValueError("No valid benchmark versions found after parsing.")

    # Sort versions (beta will automatically come last if sorted lexicographically)
    versions.sort(reverse=True)

    # Return the latest version
    return versions[0]


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
    """Get the current installed Adobe Premiere Pro version string."""
    base_path = "C:\\Program Files\\Adobe"
    
    # Look for Adobe Premiere Pro folders
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe Photoshop" in d],
        reverse=True  # Prioritize newer versions
    )
    
    for folder in possible_versions:
        exe_path = os.path.join(base_path, folder, "Photoshop.exe")
        if os.path.exists(exe_path):
            try:
                lang, codepage = win32api.GetFileVersionInfo(
                    exe_path, "\\VarFileInfo\\Translation"
                )[0]
                str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                return win32api.GetFileVersionInfo(exe_path, str_info_path)
            except Exception as e:
                print(f"Error reading version from {exe_path}: {e}")
    
    return None  # No valid installation found

def get_aftereffects_version() -> str:
    """Get the installed Adobe After Effects version string, prioritizing Beta versions."""
    base_path = r"C:\Program Files\Adobe"

    # Check if Adobe folder exists
    if not os.path.exists(base_path):
        print("Adobe directory not found.")
        return None

    # Look for After Effects folders (including Beta)
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe After Effects" in d],
        key=lambda x: ("Beta" not in x, x),  # Beta prioritized
        reverse=True  # Ensures newer versions come first
    )

    for folder in possible_versions:
        support_files_path = os.path.join(base_path, folder, "Support Files")

        # Check both standard and beta executables
        exe_candidates = ["AfterFX (Beta).exe", "AfterFX.exe"]  # Prioritize Beta
        for exe_name in exe_candidates:
            exe_path = os.path.join(support_files_path, exe_name)
            if os.path.exists(exe_path):
                try:
                    info = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")
                    if info:
                        lang, codepage = info[0]
                        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                        return str(win32api.GetFileVersionInfo(exe_path, str_info_path))
                except Exception as e:
                    print(f"Error reading version from {exe_path}: {e}")

    return None  # No valid installation found


def get_premierepro_version() -> str:
    """Get the current installed Adobe Premiere Pro version string."""
    base_path = "C:\\Program Files\\Adobe"
    
    # Look for Adobe Premiere Pro folders
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe Premiere Pro" in d],
        reverse=True  # Prioritize newer versions
    )
    
    for folder in possible_versions:
        exe_path = os.path.join(base_path, folder, "Adobe Premiere Pro.exe")
        if os.path.exists(exe_path):
            try:
                lang, codepage = win32api.GetFileVersionInfo(
                    exe_path, "\\VarFileInfo\\Translation"
                )[0]
                str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                return win32api.GetFileVersionInfo(exe_path, str_info_path)
            except Exception as e:
                print(f"Error reading version from {exe_path}: {e}")
    
    return None  # No valid installation found


def get_davinci_version() -> str:
    """get current photoshop version string"""
    path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\Resolve.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(path, str_info_path)
    except Exception as e:
        print(e)
    return None

def get_pugetbench_version() -> str:
    """get current premiere pro version string"""
    path = "C:\\Program Files\\PugetBench for Creators\\PugetBench for Creators.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation")[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(path, str_info_path)
    except Exception as e:
        print(e)
    return None