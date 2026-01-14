import logging

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, int_time, press, sleep
from harness_utils.screenshot import Screenshotter


def run_benchmark(sc: Screenshotter, am: ArtifactManager) -> tuple[int, int]:
    sleep(20)

    if not find_word(sc, "new", "Did not see main menu.", timeout = 30):
        return (0, 0)

    if not navigate_settings(sc, am):
        return (0, 0)

    if not find_word(sc, "fps", "Benchmark didn't start.", timeout = 30):
        return (0, 0)

    test_start_time = int_time() - 5

    logging.info("Benchmark started. Waiting for benchmark to complete.")
    
    sleep(70)  # could be made into an editable const

    if not find_word(sc, "results", "Did not see results screen."):
        return (0, 0)

    am.take_screenshot(
        "results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark"
    )

    test_end_time = int_time() - 2

    return test_start_time, test_end_time


def navigate_settings(sc: Screenshotter, am: ArtifactManager) -> bool:
    """Simulate inputs to navigate the main menu"""

    logging.info("Navigating main menu")

    # navigating to settings menu
    if not find_word(sc, "continue"):
        # an account with no save game has less menu options, so just press left and enter settings
        press("left,enter")
    else:
        press("left,down,enter")

    if not find_word(sc, "volume", "Did not see volume options"):
        return False

    # entered settings
    press("3*3")

    if not find_word(sc, "preset"):
        return False

    # now on graphics tab
    am.take_screenshot("graphics_1.png", ArtifactType.CONFIG_IMAGE, "graphics menu 1")

    press("down*2")

    # gets you to film grain
    if find_word(sc, "dlss"):
        if find_word(sc, "multi"):
            press("down")
        press("down*2")

        # gets you to film grain usually except for combined with RT

        if not find_word(sc, "grain"):
            press("down")

    # fsr
    if find_word(sc, "amd"):
        press("down")  # gets you to film grain

    # xess
    if find_word(sc, "xess"):
        press("down")  # gets you to film grain

    logging.info("check for rt")
    if find_word(sc, "reflections"):
        press("down*3")
        am.take_screenshot(
            "graphics_rt.png", ArtifactType.CONFIG_IMAGE, "graphics menu rt"
        )
    elif find_word(sc, "path"):
        press("down")
        am.take_screenshot(
            "graphics_pt.png",
            ArtifactType.CONFIG_IMAGE,
            "graphics menu path tracing",
        )

    press("down*7")

    if not find_word(sc, "anisotropy"):
        return False

    am.take_screenshot("graphics_2.png", ArtifactType.CONFIG_IMAGE, "graphics menu 2")

    press("down*11")

    if not find_word(sc, "occlusion"):
        return False

    am.take_screenshot("graphics_3.png", ArtifactType.CONFIG_IMAGE, "graphics menu 3")

    press("down*3")

    if not find_word(sc, "level"):
        return False

    am.take_screenshot("graphics_4.png", ArtifactType.CONFIG_IMAGE, "graphics menu 4")

    press("3")

    if not find_word(sc, "resolution"):
        return False

    # now on video tab
    am.take_screenshot("video.png", ArtifactType.CONFIG_IMAGE, "video menu")

    press("b, enter")

    return True
