"""Platform detection helpers."""

import logging
import platform

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    """Return True when running on Windows."""
    current_os = platform.system()
    result = current_os == "Windows"
    logger.debug("Checking Windows platform: os=%s result=%s", current_os, result)
    return result


def is_linux() -> bool:
    """Return True when running on Linux."""
    current_os = platform.system()
    result = current_os == "Linux"
    logger.debug("Checking Linux platform: os=%s result=%s", current_os, result)
    return result
