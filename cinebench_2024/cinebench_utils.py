"""Utility functions for Cinebench 2024 test script"""
import re

SCORE_PATTERN = re.compile(r"^CB (\d+\.\d+) \(.+\)$")

def get_score(output: str) -> str | None:
    """Finds score pattern from output string"""
    for line in reversed(output.splitlines()):
        match = SCORE_PATTERN.search(line)
        if match:
            return match.group(1)

    return None
