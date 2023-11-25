"""Functions related to managing processes"""
import psutil

def terminate_processes(*process_names: str) -> None:
    """Finds given process names and terminates them"""
    for name in process_names:
        for process in psutil.process_iter():
            if name.lower() in process.name().lower():
                process.terminate()
