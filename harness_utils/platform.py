"""Platform detection helpers."""

import platform


def is_windows() -> bool:
    """Return True when running on Windows."""
    return platform.system() == "Windows"


def is_linux() -> bool:
    """Return True when running on Linux."""
    return platform.system() == "Linux"


def require_windows(feature: str) -> None:
    """Raise RuntimeError when a feature requires Windows but is not on Windows."""
    if not is_windows():
        raise RuntimeError(f"{feature} requires Windows; current OS is {platform.system()}")


def require_linux(feature: str) -> None:
    """Raise RuntimeError when a feature requires Linux but is not on Linux."""
    if not is_linux():
        raise RuntimeError(f"{feature} requires Linux; current OS is {platform.system()}")
