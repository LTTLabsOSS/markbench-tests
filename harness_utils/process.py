"""Functions related to managing processes"""

import logging

import psutil

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)


def terminate_process(process_name: str) -> None:
    """Finds a given process name and terminates it"""
    if not process_name:
        logger.debug("No process name provided")
        return

    logger.debug("Terminating process: %s", process_name)
    if is_windows():
        for process in psutil.process_iter(["pid", "name"]):
            process_name_current = process.info.get("name") or ""
            if process_name in process_name_current:
                logger.debug(
                    "Terminating process pid=%s name=%s",
                    process.info.get("pid"),
                    process_name_current,
                )
                try:
                    process.terminate()
                except psutil.Error as err:
                    logger.warning("Failed to terminate process: %s", err)
        logger.debug("Process termination complete")
        return

    if is_linux():
        process_name_lower = process_name.lower()
        for process in psutil.process_iter(["pid", "name", "cmdline"]):
            command = " ".join(process.info.get("cmdline") or [])

            if process_name_lower in command.lower():
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
                return

        logger.debug("Process not found: %s", process_name)
        return

    logger.warning("Process termination unsupported on this platform")


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None
