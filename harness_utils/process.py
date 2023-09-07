import psutil

def terminate_processes(*process_names: str) -> None:
    for name in process_names:
        for process in psutil.process_iter():
            if name.lower() in process.name().lower():
                process.terminate()