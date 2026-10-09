"""godot compile utility functions"""

import ctypes
import logging
import os
import shutil
import subprocess
import time
from ctypes import wintypes
from datetime import timedelta
from pathlib import Path
from zipfile import ZipFile

logger = logging.getLogger(__name__)

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
MINICONDA_INSTALLER = "Miniconda3-24.5.0-0-Windows-x86_64.exe"
# godot and llvm-mingw versions are pinned together: newer compilers can fail
# on an older godot's bundled third-party code (godot 4.4.1 fails on LLVM 23).
# change both together and test a full build before updating either.
GODOT_VERSION = "4.7.2-stable"
# llvm-mingw 20261006 = LLVM 23.1.3
# zips: https://github.com/mstorsjo/llvm-mingw/releases/tag/20261006
LLVM_MINGW_RELEASE = "20261006"
LLVM_MINGW_NETWORK_DIRECTORY = Path(
    "\\\\labs.lmg.gg\\labs\\01_Installers_Utilities\\llvm-mingw\\"
)
# llvm-mingw zip suffix for each host architecture. each zip runs on that
# host and can build for every target architecture
LLVM_MINGW_HOSTS = {
    "x86_64": "x86_64",
    "arm64": "aarch64",
}
# IsWow64Process2 native machine values
IMAGE_FILE_MACHINES = {
    0x8664: "x86_64",
    0xAA64: "arm64",
}
# target triple godot uses to look up mingw tools for each target architecture
LLVM_MINGW_TRIPLES = {
    "x86_64": "x86_64-w64-mingw32",
    "arm64": "aarch64-w64-mingw32",
}
MINICONDA_EXECUTABLE_PATH = Path("C:\\ProgramData\\miniconda3\\_conda.exe")
CONDA_ENV_NAME = "godotbuild"
GODOT_DIR = f"godot-{GODOT_VERSION}"
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
        # godot reads these to guess the build arch and errors out when
        # cross-compiling from an msys2/git bash or vs developer shell
        "MSYSTEM",
        "VCTOOLSINSTALLDIR",
    ]:
        env.pop(key, None)
    return env


def run_subprocess(command: list[str], cwd: Path | None = None) -> str:
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


def detect_host_architecture() -> str:
    """
    returns the native cpu architecture of this machine. uses IsWow64Process2
    because an x86_64 python running under emulation on arm64 reports x86_64
    from platform.machine()
    """
    process_machine = ctypes.c_ushort()
    native_machine = ctypes.c_ushort()
    kernel32 = ctypes.windll.kernel32
    # declare types so the 64-bit process handle isn't truncated to an int
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.IsWow64Process2.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_ushort),
        ctypes.POINTER(ctypes.c_ushort),
    ]
    kernel32.IsWow64Process2.restype = wintypes.BOOL
    if not kernel32.IsWow64Process2(
        kernel32.GetCurrentProcess(),
        ctypes.byref(process_machine),
        ctypes.byref(native_machine),
    ):
        raise Exception("IsWow64Process2 failed, could not detect host architecture")
    host = IMAGE_FILE_MACHINES.get(native_machine.value)
    if host is None:
        raise Exception(f"unsupported host architecture: {native_machine.value:#x}")
    return host


def get_llvm_mingw_name(host: str) -> str:
    """returns the llvm-mingw release name for the given host architecture"""
    return f"llvm-mingw-{LLVM_MINGW_RELEASE}-ucrt-{LLVM_MINGW_HOSTS[host]}"


def get_llvm_mingw_folder(host: str) -> Path:
    """returns the local llvm-mingw folder for the given host architecture"""
    return SCRIPT_DIRECTORY.joinpath(get_llvm_mingw_name(host))


def install_llvm_mingw(host: str) -> str:
    """copies llvm-mingw for the host from the network drive and adds to path"""
    folder = get_llvm_mingw_folder(host)
    clang_path = folder.joinpath("bin", "clang.exe")
    logger.info("checking for existing llvm-mingw at %s", clang_path)
    message = "existing llvm-mingw installation detected"
    if not clang_path.is_file():
        zip_name = f"{get_llvm_mingw_name(host)}.zip"
        source = LLVM_MINGW_NETWORK_DIRECTORY.joinpath(zip_name)
        destination = SCRIPT_DIRECTORY.joinpath(zip_name)

        logger.info("checking network drive for %s", source)
        if not source.is_file():
            raise Exception(f"llvm-mingw zip not found on network drive: {source}")
        size_mb = source.stat().st_size / (1024 * 1024)

        logger.info("copying %.1f MB to %s", size_mb, destination)
        step_start = time.time()
        shutil.copyfile(source, destination)
        logger.info("copy finished in %.1f seconds", time.time() - step_start)

        logger.info("extracting %s to %s", zip_name, SCRIPT_DIRECTORY)
        step_start = time.time()
        with ZipFile(destination, "r") as zip_object:
            members = zip_object.infolist()
            for index, member in enumerate(members, start=1):
                zip_object.extract(member, path=SCRIPT_DIRECTORY)
                if index % 2000 == 0:
                    logger.info("extracted %d of %d files", index, len(members))
        logger.info(
            "extracted %d files in %.1f seconds",
            len(members),
            time.time() - step_start,
        )

        if not clang_path.is_file():
            raise Exception(f"clang.exe not found after extraction: {clang_path}")
        message = "installed llvm-mingw from network drive"
    original_path = os.environ.get("PATH", "")
    if str(folder) not in original_path:
        logger.info("adding %s to PATH", folder.joinpath("bin"))
        os.environ["PATH"] = str(folder.joinpath("bin")) + os.pathsep + original_path
    return message


def get_compiler_version(host: str, target: str) -> str:
    """
    returns the first line of the clang version output, after checking that
    the clang godot will find on PATH for the target is the bundled llvm-mingw
    one. if godot can't find clang it silently falls back to any gcc on PATH,
    so fail early.
    """
    clang_name = f"{LLVM_MINGW_TRIPLES[target]}-clang"
    found = shutil.which(clang_name, path=get_conda_subprocess_env().get("PATH"))
    expected_bin = get_llvm_mingw_folder(host).joinpath("bin")
    if found is None or Path(found).resolve().parent != expected_bin.resolve():
        raise Exception(
            f"{clang_name} on PATH is {found}, expected it in {expected_bin}"
        )
    clang_path = Path(found)
    try:
        output = subprocess.check_output(
            [str(clang_path), "--version"], stderr=subprocess.STDOUT, text=True
        )
    except Exception as err:
        raise Exception(f"could not get compiler version from {clang_path}") from err
    return output.splitlines()[0].strip()


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
        f'"{SCRIPT_DIRECTORY.joinpath(MINICONDA_INSTALLER)!s}"',
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
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode not in (0, 1):
        command_string = " ".join(command)
        error_output = (process.stdout or process.stderr or "").strip()
        if error_output:
            raise Exception(f"command failed: {command_string}\n{error_output}")
        raise Exception(f"command failed: {command_string}")
    return process.returncode != 1


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


def run_conda_command(conda_cmd: list[str]) -> str:
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
