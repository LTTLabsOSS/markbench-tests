"""Platform detection helpers."""

import platform


def is_windows() -> bool:
    """Return True when running on Windows."""
    return platform.system() == "Windows"


def is_linux() -> bool:
    """Return True when running on Linux."""
    return platform.system() == "Linux"
