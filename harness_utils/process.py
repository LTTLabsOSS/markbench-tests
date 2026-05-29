"""Functions related to managing processes"""

import logging

import psutil

from harness_utils.platform import is_linux, is_windows

logger = logging.getLogger(__name__)


def terminate_process(process_name: str) -> None:
    """Finds a given process name and terminates it"""
    if not process_name:
        logger.info("Skipping process termination for empty process name")
        return

    logger.info("Terminating process_name=%s", process_name)
    process_name_lower = process_name.casefold()

    if is_windows():
        matches = 0
        for process in psutil.process_iter():
            process_name_current = process.name()
            if process_name_lower in process_name_current.casefold():
                logger.info(
                    "Terminating Windows process pid=%s name=%s",
                    process.pid,
                    process_name_current,
                )
                process.terminate()
                matches += 1
        logger.info("Windows process termination complete matches=%s", matches)
        return

    if is_linux():
        processes = []
        for process in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
            cmdline = process.info.get("cmdline") or []
            process_text = (
                f"{process.info.get('name') or ''} "
                f"{process.info.get('exe') or ''} "
                f"{' '.join(cmdline)}"
            ).casefold()

            if process_name_lower in process_text:
                logger.info(
                    "Terminating Linux process pid=%s name=%s exe=%s",
                    process.info.get("pid"),
                    process.info.get("name"),
                    process.info.get("exe"),
                )
                process.terminate()
                processes.append(process)

        logger.info("Waiting for Linux processes to exit matches=%s", len(processes))
        _, survivors = psutil.wait_procs(processes, timeout=5)
        for process in survivors:
            logger.info("Killing Linux survivor pid=%s", process.pid)
            process.kill()
        logger.info(
            "Linux process termination complete matches=%s survivors=%s",
            len(processes),
            len(survivors),
        )
        return

    logger.warning("Process termination unsupported on this platform")


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None
