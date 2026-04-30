"""Utility functions for Cinebench 2026 test script"""


def friendly_test_name(test: str) -> str:
    """Return a friendlier string given a test argument"""
    if test == "g_CinebenchCpu1Test=true":
        return "Cinebench 2026 Single Thread"
    if test == "g_CinebenchCpuXTest=true":
        return "Cinebench 2026 Multi Threads"
    if test == "g_CinebenchGpuTest=true":
        return "Cinebench 2026 GPU"
    if test == "g_CinebenchCpuSMTTest=true":
        return "Cinebench 2026 Single SMT Core"
    return test
