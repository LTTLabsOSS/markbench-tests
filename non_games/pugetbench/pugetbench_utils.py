"""utils file for pugetbench harness"""

import csv
import json
import os
import re
from pathlib import Path

import win32api


def trim_to_major_minor(version: str | None) -> str | None:
    """Trims the versioning into major.minor."""
    if version is None:
        return None
    # Match major.minor at the start
    match = re.match(r"(\d+)\.(\d+)", version)
    if not match:
        return version  # fallback if unrecognized

    major_minor = f"{match.group(1)}.{match.group(2)}"

    # Preserve -beta suffix if present
    if "-beta" in version:
        major_minor += "-beta"

    return major_minor


def get_latest_benchmark_by_version(benchmark_name: str):
    """Get the latest benchmark version, prioritizing beta if it's newer."""
    valid_names = ["photoshop", "premierepro", "aftereffects", "lightroom", "resolve", "unreal"]
    if benchmark_name not in valid_names:
        raise ValueError("Invalid benchmark name")

    benchmark_json_dir = Path().home() / "AppData/Local/com.puget.benchmark/benchmarks"
    if not benchmark_json_dir.exists():
        raise ValueError("Could not find benchmark directory in appdata")

    # Find relevant benchmark files
    benchmark_files = [
        f
        for f in os.listdir(benchmark_json_dir)
        if f.startswith(f"{benchmark_name}-benchmark-")
    ]

    if not benchmark_files:
        raise ValueError("No valid benchmark versions found.")

    version_pattern = re.compile(r"-(\d+)\.(\d+)\.(\d+)(-beta)?(-dev)?\.json$")

    def extract_version(filename):
        """Extracts numeric version and beta or dev flag from filename."""
        match = version_pattern.search(filename)
        if match:
            major, minor, patch, beta_flag, dev_flag = match.groups()
            version = f"{major}.{minor}.{patch}"
            if beta_flag:
                version += "-beta"
            if dev_flag:
                version += "-dev"
            return version
        return None  # Ignore files that don't match

    # Extract valid versions
    versions = [extract_version(f) for f in benchmark_files]
    versions = [v for v in versions if v is not None]  # Filter out invalid matches

    if not versions:
        raise ValueError("No valid benchmark versions found after parsing.")

    # Sort numerically, with releases before beta
    def version_key(v: str):
        main = v.split("-")[0]  # take numeric part only
        nums = tuple(int(x) for x in main.split("."))
        beta_flag = 1 if "-beta" in v else 0
        return nums, -beta_flag  # release first

    versions.sort(key=version_key, reverse=True)

    # Return the latest version
    return versions[0]


def find_score_in_log(log_path, preset):
    """Return a single PugetBench overall score for the specified preset."""
    target_label = f"Overall Score ({preset})"

    with open(log_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            if not row:
                continue

            label = row[0].strip()

            if label != target_label:
                continue

            # Find the first numeric field
            for field in row:
                cleaned = field.replace(",", "").strip()
                if cleaned.isdigit():
                    return int(cleaned)

    return None


def get_photoshop_version() -> tuple[str, str]:
    """Get the installed Adobe Photoshop version string, prioritizing Beta versions."""
    base_path = r"C:\Program Files\Adobe"

    # Check if Adobe folder exists
    if not os.path.exists(base_path):
        print("Adobe directory not found.")
        return None, None

    # Look for Adobe Photoshop folders
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe Photoshop" in d],
        reverse=True,  # Prioritize newer versions
    )

    for folder in possible_versions:
        exe_path = os.path.join(base_path, folder, "Photoshop.exe")
        if os.path.exists(exe_path):
            try:
                lang, codepage = win32api.GetFileVersionInfo(
                    exe_path, "\\VarFileInfo\\Translation"
                )[0]
                str_info_path = (
                    f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                )
                full_version = win32api.GetFileVersionInfo(exe_path, str_info_path)

                # Trim to major.minor
                major_minor = trim_to_major_minor(full_version)

                return full_version, major_minor
            except Exception as e:
                print(f"Error reading version from {exe_path}: {e}")

    return None, None


def get_aftereffects_version() -> tuple[str, str]:
    """Get the installed Adobe After Effects version string, prioritizing Beta versions."""
    base_path = r"C:\Program Files\Adobe"

    # Check if Adobe folder exists
    if not os.path.exists(base_path):
        print("Adobe directory not found.")
        return None, None

    # Look for After Effects folders (including Beta)
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe After Effects" in d],
        key=lambda x: ("Beta" not in x, x),  # Beta prioritized
        reverse=True,  # Ensures newer versions come first
    )

    for folder in possible_versions:
        support_files_path = os.path.join(base_path, folder, "Support Files")

        # Check both standard and beta executables
        exe_candidates = ["AfterFX (Beta).exe", "AfterFX.exe"]  # Prioritize Beta
        for exe_name in exe_candidates:
            exe_path = os.path.join(support_files_path, exe_name)
            if os.path.exists(exe_path):
                try:
                    info = win32api.GetFileVersionInfo(
                        exe_path, "\\VarFileInfo\\Translation"
                    )
                    if info:
                        lang, codepage = info[0]
                        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                        full_version = str(
                            win32api.GetFileVersionInfo(exe_path, str_info_path)
                        )

                        # Trim to major.minor
                        major_minor = trim_to_major_minor(full_version)

                        return full_version, major_minor
                except Exception as e:
                    print(f"Error reading version from {exe_path}: {e}")

    return None, None


def get_premierepro_version() -> tuple[str, str]:
    """Get the current installed Adobe Premiere Pro version string."""
    base_path = r"C:\Program Files\Adobe"

    # Check if Adobe folder exists
    if not os.path.exists(base_path):
        print("Adobe directory not found.")
        return None, None

    # Look for Adobe Premiere Pro folders
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe Premiere Pro" in d],
        reverse=True,  # Prioritize newer versions
    )

    for folder in possible_versions:
        exe_path = os.path.join(base_path, folder, "Adobe Premiere Pro.exe")
        if os.path.exists(exe_path):
            try:
                lang, codepage = win32api.GetFileVersionInfo(
                    exe_path, "\\VarFileInfo\\Translation"
                )[0]
                str_info_path = (
                    f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                )
                full_version = win32api.GetFileVersionInfo(exe_path, str_info_path)

                # Trim to major.minor
                major_minor = trim_to_major_minor(full_version)

                return full_version, major_minor
            except Exception as e:
                print(f"Error reading version from {exe_path}: {e}")

    return None, None


def get_lightroom_version() -> tuple[str, str]:
    """Get the current installed Adobe Lightroom Classic version string."""
    base_path = r"C:\Program Files\Adobe"

    # Check if Adobe folder exists
    if not os.path.exists(base_path):
        print("Adobe directory not found.")
        return None, None

    # Look for Adobe Lightroom Classic folders
    possible_versions = sorted(
        [d for d in os.listdir(base_path) if "Adobe Lightroom Classic" in d],
        reverse=True,  # Prioritize newer versions
    )

    for folder in possible_versions:
        exe_path = os.path.join(base_path, folder, "Lightroom.exe")
        if os.path.exists(exe_path):
            try:
                lang, codepage = win32api.GetFileVersionInfo(
                    exe_path, "\\VarFileInfo\\Translation"
                )[0]
                str_info_path = (
                    f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
                )
                full_version = win32api.GetFileVersionInfo(exe_path, str_info_path)

                # Trim to major.minor
                major_minor = trim_to_major_minor(full_version)

                return full_version, major_minor
            except Exception as e:
                print(f"Error reading version from {exe_path}: {e}")

    return None, None


def get_davinci_version() -> tuple[str, str]:
    """Get the current installed Davinci Resolve Studio version string."""
    path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
    if not os.path.exists(path):
        print("DaVinci Resolve executable not found.")
        return None, None

    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        full_version = win32api.GetFileVersionInfo(path, str_info_path)

        # Trim to major.minor
        major_minor = trim_to_major_minor(full_version)

        return full_version, major_minor

    except Exception as e:
        print(f"Error reading version from {path}: {e}")
        return None, None


def get_pugetbench_version() -> str:
    """Get the current installed PugetBench version string."""
    path = "C:\\Program Files\\PugetBench for Creators\\PugetBench for Creators.exe"
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            path, "\\VarFileInfo\\Translation"
        )[0]
        str_info_path = f"\\StringFileInfo\\{lang:04X}{codepage:04X}\\ProductVersion"
        return win32api.GetFileVersionInfo(path, str_info_path)
    except Exception as e:
        print(e)
    return None

def get_unreal_version() -> tuple[str | None, str | None]:
    """Get the installed Unreal Engine version string."""

    manifest_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"

    if not os.path.isdir(manifest_dir):
        print("Epic Games Launcher manifest directory not found.")
        return None, None

    # Look through Epic Launcher manifests for Unreal Engine installations.
    for filename in os.listdir(manifest_dir):
        if not filename.endswith(".item"):
            continue

        manifest_path = os.path.join(manifest_dir, filename)

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        # Unreal Engine manifests have an AppName such as UE_5.6
        app_name = manifest.get("AppName", "")

        if not app_name.startswith("UE_"):
            continue

        install_location = manifest.get("InstallLocation")

        if not install_location:
            continue

        # Normalize the path in case the manifest uses forward slashes.
        install_location = os.path.normpath(install_location)

        build_version_path = os.path.join(
            install_location,
            "Engine",
            "Build",
            "Build.version",
        )

        if not os.path.isfile(build_version_path):
            continue

        try:
            with open(build_version_path, "r", encoding="utf-8") as f:
                version = json.load(f)

            major = version["MajorVersion"]
            minor = version["MinorVersion"]
            patch = version["PatchVersion"]

            full_version = f"{major}.{minor}.{patch}"
            major_minor = f"{major}.{minor}"

            return full_version, major_minor

        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Error reading Unreal version from {build_version_path}: {e}")

    print("Unreal Engine installation not found.")
    return None, None