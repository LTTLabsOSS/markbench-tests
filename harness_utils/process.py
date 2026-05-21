"""Functions related to managing processes"""

import logging

import psutil

logger = logging.getLogger(__name__)


def _normalize_name(process_name: str | None) -> str:
    return (process_name or "").casefold()


def _name_variants(process_name: str) -> set[str]:
    normalized_name = _normalize_name(process_name)
    variants = {normalized_name}
    if normalized_name.endswith(".exe"):
        variants.add(normalized_name[:-4])
    else:
        variants.add(f"{normalized_name}.exe")
    return variants


def _iter_processes():
    for process in psutil.process_iter(["pid", "name"]):
        try:
            name = process.info.get("name") or process.name()
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        if not name:
            continue
        yield process, name


def _matches_exact(name: str, target: str) -> bool:
    return _normalize_name(name) in _name_variants(target)


def _matches_substring(name: str, target: str) -> bool:
    normalized_name = _normalize_name(name)
    return any(variant in normalized_name for variant in _name_variants(target))


def _find_processes(process_name: str) -> list[tuple[psutil.Process, str]]:
    processes = list(_iter_processes())
    exact_matches = [
        (process, name) for process, name in processes if _matches_exact(name, process_name)
    ]
    if exact_matches:
        return exact_matches
    return [
        (process, name)
        for process, name in processes
        if _matches_substring(name, process_name)
    ]


def terminate_processes(*process_names: str) -> None:
    """Finds given process names and terminates them"""
    terminated_pids: set[int] = set()
    for name in process_names:
        for process, process_name in _find_processes(name):
            if process.pid in terminated_pids:
                continue
            try:
                logger.info("Terminating process pid=%s name=%s", process.pid, process_name)
                process.terminate()
                terminated_pids.add(process.pid)
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue


def is_process_running(process_name):
    """check if given process is running"""
    matches = _find_processes(process_name)
    if matches:
        return matches[0][0]
    return None
