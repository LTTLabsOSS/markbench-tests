"""Time unit conversion helpers for harnesses."""


def seconds_to_milliseconds(seconds: float | int) -> int:
    """Convert seconds to milliseconds."""
    return round(seconds * 1000)
