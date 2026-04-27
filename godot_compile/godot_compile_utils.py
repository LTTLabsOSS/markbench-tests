"""godot compile utility functions"""

import os
import shutil
import subprocess
import time
from datetime import timedelta
from pathlib import Path
from typing import List
from zipfile import ZipFile

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
MINICONDA_INSTALLER = "Miniconda3-24.5.0-0-Windows-x86_64.exe"
MINGW_ZIP = "x86_64-13.2.0-release-posix-seh-msvcrt-rt_v11-rev1.zip"
MINGW_FOLDER = SCRIPT_DIRECTORY.joinpath("mingw64")
MINICONDA_EXECUTABLE_PATH = Path("C:\\ProgramData\\miniconda3\\_conda.exe")
CONDA_ENV_NAME = "godotbuild"
GODOT_DIR = "godot-4.4.1-stable"
CONDA_ENV_DIRECTORY = Path.home().joinpath(".conda", "envs", CONDA_ENV_NAME)
CONDA_ENV_PYTHON = CONDA_ENV_DIRECTORY.joinpath("python.exe")


def get_conda_subprocess_env() -> dict[str, str]:
    """build an isolated subprocess environment for conda-managed Python"""
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    for key in [
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONEXECUTABLE",
        "PYTHONUSERBASE",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_PROMPT_MODIFIER",
        "__PYVENV_LAUNCHER__",
    ]:
        env.pop(key, None)
    return env


def run_subprocess(command: List[str], cwd: Path | None = None) -> str:
    """run a subprocess and surface stdout/stderr on failure"""
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=get_conda_subprocess_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        output = (err.stdout or "").strip()
        command_string = " ".join(command)
        if output:
            raise Exception(f"command failed: {command_string}\n{output}") from err
        raise Exception(f"command failed: {command_string}") from err
    return completed.stdout


def install_mingw() -> str:
    """copies mingw from the network drive and adds to path"""
    original_path = os.environ.get("PATH", "")
    if MINGW_FOLDER.is_dir():
        if str(MINGW_FOLDER) not in original_path:
            os.environ["PATH"] = (
                str(MINGW_FOLDER.joinpath("bin")) + os.pathsep + original_path
            )
        return "existing mingw installation detected"
    source = Path("\\\\labs.lmg.gg\\labs\\01_Installers_Utilities\\MinGW\\").joinpath(
        MINGW_ZIP
    )
    destination = SCRIPT_DIRECTORY.joinpath(MINGW_ZIP)
    shutil.copyfile(source, destination)
    with ZipFile(destination, "r") as zip_object:
        zip_object.extractall(path=SCRIPT_DIRECTORY)
    if str(MINGW_FOLDER) not in original_path:
        os.environ["PATH"] = (
            str(MINGW_FOLDER.joinpath("bin")) + os.pathsep + original_path
        )
    return "installed mingw from network drive"


def copy_miniconda_from_network_drive():
    """copies miniconda installer from network drive"""
    source = Path(
        "\\\\labs.lmg.gg\\labs\\01_Installers_Utilities\\Miniconda\\"
    ).joinpath(MINICONDA_INSTALLER)
    destination = SCRIPT_DIRECTORY.joinpath(MINICONDA_INSTALLER)
    shutil.copyfile(source, destination)


def install_miniconda() -> str:
    """installs miniconda from the network drive, returns install process output"""
    if MINICONDA_EXECUTABLE_PATH.exists():
        return "existing miniconda installation detected"
    try:
        copy_miniconda_from_network_drive()
    except Exception as err:
        raise Exception("could not copy miniconda from network drive") from err
    command = [
        "powershell",
        "start-process",
        "-FilePath",
        f'"{str(SCRIPT_DIRECTORY.joinpath(MINICONDA_INSTALLER))}"',
        "-ArgumentList",
        '"/S"',
        "-Wait",
    ]
    try:
        output = subprocess.check_output(
            command,
            env=get_conda_subprocess_env(),
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as err:
        command_string = " ".join(command)
        raise Exception(
            f"could not install miniconda using command {command_string}"
        ) from err
    return output


def copy_godot_source_from_network_drive() -> str:
    """copies godot source files from the network drive"""
    if SCRIPT_DIRECTORY.joinpath(GODOT_DIR).is_dir():
        return "existing godot source directory detected"
    zip_name = f"{GODOT_DIR}.zip"
    source = Path("\\\\labs.lmg.gg\\labs\\03_ProcessingFiles\\Godot Files\\").joinpath(
        zip_name
    )
    destination = SCRIPT_DIRECTORY.joinpath(zip_name)
    shutil.copyfile(source, destination)
    with ZipFile(destination, "r") as zip_object:
        try:
            zip_object.extractall(path=SCRIPT_DIRECTORY)
        except Exception as ex:
            raise Exception("error extracting godot zip") from ex
        return "godot source copied and unpacked from network drive"


def check_conda_environment_exists() -> bool:
    """check if godotbuild environment exists"""
    command = [str(MINICONDA_EXECUTABLE_PATH), "list", "-n", CONDA_ENV_NAME]
    process = subprocess.run(
        command,
        env=get_conda_subprocess_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if process.returncode not in (0, 1):
        command_string = " ".join(command)
        error_output = (process.stdout or process.stderr or "").strip()
        if error_output:
            raise Exception(f"command failed: {command_string}\n{error_output}")
        raise Exception(f"command failed: {command_string}")
    if process.returncode == 1:
        return False
    return True


def remove_conda_environment() -> str:
    """remove the godotbuild environment if it already exists"""
    if not check_conda_environment_exists():
        return "godotbuild conda environment did not exist"
    command = [
        str(MINICONDA_EXECUTABLE_PATH),
        "env",
        "remove",
        "-n",
        CONDA_ENV_NAME,
        "-y",
    ]
    output = run_subprocess(command)
    return output or "removed existing godotbuild conda environment"


def create_conda_environment() -> str:
    """recreate the conda environment from scratch for each run"""
    output_lines = [remove_conda_environment().strip()]
    command = [
        str(MINICONDA_EXECUTABLE_PATH),
        "create",
        "-n",
        CONDA_ENV_NAME,
        "python=3.11",
        "-y",
    ]
    output_lines.append(run_subprocess(command).strip())
    return "\n".join(line for line in output_lines if line)


def run_conda_command(conda_cmd: List[str]) -> str:
    """run a command using the conda environment's interpreter"""
    command = [str(CONDA_ENV_PYTHON)] + conda_cmd
    output = run_subprocess(command, cwd=SCRIPT_DIRECTORY.joinpath(GODOT_DIR))
    return output


def convert_duration_string_to_seconds(duration: str) -> int:
    """convert duration in HH:MM:SS.xxx format to total seconds"""
    time_obj = timedelta(
        hours=int(duration.split(":")[0]),
        minutes=int(duration.split(":")[1]),
        seconds=float(duration.split(".")[0].split(":")[2]),
        milliseconds=int(float("0." + duration.split(".")[1]) * 1000),
    )

    return round(time_obj.total_seconds())


def current_time_ms():
    """Get current timestamp in milliseconds since epoch"""
    return int(time.time() * 1000)
