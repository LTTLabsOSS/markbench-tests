import logging
import os
from subprocess import Popen
import shutil

from pathlib import Path

DEFAULT_BASE_PATH = os.path.join(os.environ["ProgramFiles(x86)"], "RivaTuner Statistics Server")
DEFAULT_EXECUTABLE_NAME = "RTSS.exe"
DEFAULT_EXECUTABLE_PATH = os.path.join(DEFAULT_BASE_PATH, DEFAULT_EXECUTABLE_NAME)
DEFAULT_PROFILES_PATH = os.path.join(DEFAULT_BASE_PATH, "Profiles")


def copy_rtss_profile(profile_path: str, rtss_profiles_directory: str = DEFAULT_PROFILES_PATH) -> None:
    # Validate path of profile we want to copy over
    is_valid_profile = os.path.isfile(profile_path)

    if not is_valid_profile:
        raise Exception(f"Can't find provided profile: {profile_path}")

    # Validate/create path to directory where we will copy profile to
    try:
        Path(rtss_profiles_directory).mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logging.error("Could not create rtss profiles directory - likely due to non-directory file existing at path.")
        raise e

    # Copy the profile over
    destination_file = os.path.join(rtss_profiles_directory, os.path.basename(profile_path))
    logging.info(F"Copying: {profile_path} -> {destination_file}")
    shutil.copy(profile_path, destination_file)


def start_rtss_process(executable_path: str = DEFAULT_EXECUTABLE_PATH) -> any:
    if not os.path.isfile(executable_path):
        raise Exception("RTSS is not installed!")

    logging.info(executable_path)
    return Popen(executable_path)

