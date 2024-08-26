"""godot compile utility functions"""
import os
from pathlib import Path
import shutil
import subprocess
from typing import List
from zipfile import ZipFile
from datetime import timedelta


SCRIPT_DIR = Path(__file__).resolve().parent
MINICONDA_INSTALLER = "Miniconda3-24.5.0-0-Windows-x86_64.exe"
MINGW_ZIP = "x86_64-13.2.0-release-posix-seh-msvcrt-rt_v11-rev1.zip"
MINGW_FOLDER = SCRIPT_DIR.joinpath("mingw64")
MINICONDA_EXECUTABLE_PATH = Path("C:\\ProgramData\\miniconda3\\_conda.exe")
CONDA_ENV_NAME = "godotbuild"
GODOT_DIR = "godot-4.3-stable"


def install_mingw() -> str:
    """copies mingw from the network drive and adds to path"""
    original_path = os.environ.get('PATH', '')
    if MINGW_FOLDER.is_dir():
        if str(MINGW_FOLDER) not in original_path:
            os.environ['PATH'] = str(MINGW_FOLDER.joinpath('bin')) + os.pathsep + original_path
        return "existing mingw installation detected"
    source = Path("\\\\Labs\\labs\\01_Installers_Utilities\\MinGW\\").joinpath(MINGW_ZIP)
    destination = SCRIPT_DIR.joinpath(MINGW_ZIP)
    shutil.copyfile(source, destination)
    with ZipFile(destination, 'r') as zip_object:
        zip_object.extractall(path=SCRIPT_DIR)
    if str(MINGW_FOLDER) not in original_path:
        os.environ['PATH'] = str(MINGW_FOLDER.joinpath('bin')) + os.pathsep + original_path
    return "installed mingw from network drive"


def copy_miniconda_from_network_drive():
    """copies miniconda installer from network drive"""
    source = Path("\\\\Labs\\labs\\01_Installers_Utilities\\Miniconda\\").joinpath(MINICONDA_INSTALLER)
    destination = SCRIPT_DIR.joinpath(MINICONDA_INSTALLER)
    shutil.copyfile(source, destination)


def install_miniconda() -> str:
    """installs miniconda from the network drive, returns install process output"""
    if MINICONDA_EXECUTABLE_PATH.exists():
        return "existing miniconda installation detected"
    copy_miniconda_from_network_drive()
    command =[
        "powershell"
        "start", 
        "/wait",
        MINICONDA_INSTALLER,
        "/InstallationType=AllUsers",
        "/AddToPath=1"]
    output = subprocess.check_output(command, stderr=subprocess.PIPE, text=True)
    return output


def copy_godot_source_from_network_drive() -> str:
    """copies godot source files from the network drive"""
    if SCRIPT_DIR.joinpath(GODOT_DIR).is_dir():
        return "existing godot source directory detected"
    zip_name = f"{GODOT_DIR}.zip"
    source = Path("\\\\Labs\\labs\\03_ProcessingFiles\\Godot Files\\").joinpath(zip_name)
    destination = SCRIPT_DIR.joinpath(zip_name)
    shutil.copyfile(source, destination)
    with ZipFile(destination, 'r') as zip_object:
        try:
            zip_object.extractall(path=SCRIPT_DIR)
        except Exception as ex:
            raise Exception ("error extracting godot zip") from ex
        return "godot source copied and unpacked from network drive"


def check_conda_environment_exists() -> bool:
    """check if godotbuild environment exists"""
    command = [
        MINICONDA_EXECUTABLE_PATH,
        "list",
        "-n",
        CONDA_ENV_NAME
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    if process.returncode == 1:
        return False
    return True


def create_conda_environment() -> str:
    """create conda environment to work in"""
    if check_conda_environment_exists():
        return "godotbuild conda environment exists"
    command = [
        MINICONDA_EXECUTABLE_PATH,
        "create",
        "-n",
        CONDA_ENV_NAME,
        "python=3.11"
    ]
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    return output


def run_conda_command(conda_cmd: List[str]) -> str:
    """run a command inside a conda environment, returns captured output from the command"""
    command = [
        MINICONDA_EXECUTABLE_PATH,
        "run",
        "-n",
        "godotbuild",
        "--cwd",
        str(SCRIPT_DIR.joinpath(GODOT_DIR)),
    ] + conda_cmd
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
    return output


def convert_duration_string_to_seconds(duration: str) -> int:
    """convert duration in HH:MM:SS.xxx format to total seconds"""
    time_obj = timedelta(
        hours=int(duration.split(':')[0]),
        minutes=int(duration.split(':')[1]),
        seconds=float(duration.split('.')[0].split(':')[2]),
        milliseconds=int(float('0.' + duration.split('.')[1])*1000))

    return round(time_obj.total_seconds())
