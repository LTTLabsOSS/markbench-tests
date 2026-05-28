"""Functions related to managing processes"""

import psutil

from harness_utils.platform import is_linux, is_windows


def terminate_process(process_name: str) -> None:
    """Finds a given process name and terminates it"""
    if not process_name:
        return

    process_name_lower = process_name.casefold()

    if is_windows():
        for process in psutil.process_iter():
            if process_name_lower in process.name().casefold():
                process.terminate()
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
                process.terminate()
                processes.append(process)

        _, survivors = psutil.wait_procs(processes, timeout=5)
        for process in survivors:
            process.kill()


def is_process_running(process_name):
    """check if given process is running"""
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None
