"""Functions related to managing processes"""

import logging
import subprocess

import psutil

from harness_utils.platform import is_windows

logger = logging.getLogger(__name__)


def terminate_process(process_name: str) -> None:
    """Finds a given process name and terminates it"""
    if not process_name:
        logger.debug("No process name provided")
        return

    logger.debug("Terminating process: %s", process_name)
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        if is_windows():
            command = process.info.get("name") or ""
        else:
            command = " ".join(process.info.get("cmdline") or [])

        if process_name.lower() in command.lower():
            logger.debug(
                "Terminating process pid=%s name=%s command=%s",
                process.info.get("pid"),
                process.info.get("name"),
                command,
            )
            try:
                process.terminate()
            except psutil.Error as err:
                logger.warning("Failed to terminate process: %s", err)

    logger.debug("Process termination complete")


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        process_name_current = process.info.get("name") or ""
        if process_name_current.lower() == process_name.lower():
            return process
    return None


def bring_process_front(process_name):
    """bring the process to foreground"""
    target_process = is_process_running(process_name)
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            f"(New-Object -ComObject WScript.Shell).AppActivate({target_process.pid})",
        ],
        check=False,
    )
