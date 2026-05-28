"""Functions related to managing processes"""

import psutil

from harness_utils.platform import is_linux, is_windows


def _terminate_processes_windows(*process_names: str) -> None:
    for name in process_names:
        for process in psutil.process_iter():
            if name.lower() in process.name().lower():
                process.terminate()


def _terminate_processes_linux(*process_names: str) -> None:
    pass


def terminate_processes(*process_names: str) -> None:
    """Finds given process names and terminates them"""
    if is_windows():
        _terminate_processes_windows(*process_names)
    elif is_linux():
        _terminate_processes_linux(*process_names)


def _is_process_running_windows(process_name):
    for process in psutil.process_iter(["pid", "name"]):
        if process.info["name"] == process_name:
            return process
    return None


def _is_process_running_linux(process_name):
    pass


def is_process_running(process_name):
    """check if given process is running"""
    if is_windows():
        return _is_process_running_windows(process_name)
    if is_linux():
        return _is_process_running_linux(process_name)
    return None
