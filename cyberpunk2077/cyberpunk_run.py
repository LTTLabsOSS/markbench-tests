import logging

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, int_time, press, sleep
from harness_utils.screenshot import Screenshotter


def run_benchmark(sc: Screenshotter, am: ArtifactManager) -> tuple[int, int]:
    sleep(15)

    if not navigate_settings(sc, am):
        return (0, 0)

    if not find_word(sc, "fps", "Benchmark didn't start.", timeout=30):
        return (0, 0)

    test_start_time = int_time() - 4

    logging.info("Benchmark started. Waiting for benchmark to complete.")

    sleep(70)  # make into an editable const, adjust timings

    if not find_word(sc, "results", "Did not see results screen."):
        return (0, 0)

    test_end_time = int_time()

    am.take_screenshot(
        "results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark"
    )

    return test_start_time, test_end_time


def navigate_settings(sc: Screenshotter, am: ArtifactManager) -> bool:
    """Simulate inputs to navigate the main menu"""

    logging.info("Navigating main menu")

    if not find_word(sc, "new", "Did not see main menu.", timeout=30):
        return False

    # navigating to settings menu
    if not find_word(sc, "continue"):
        # an account with no save game
        press("left,enter")
    else:
        press("left,down,enter")

    if not find_word(sc, "volume", "Did not see settings menu"):
        return False

    # entered settings
    press("3*3")

    if not find_word(sc, "preset"):
        return False

    # now on graphics tab

    am.take_screenshot(
        "2_graphics_preset.png", ArtifactType.CONFIG_IMAGE, "graphics preset"
    )

    press("down*2")

    if not find_word(sc, "grain"):
        if not find_word(sc, "reflections"):
            # RT off
            # Resolution Scaling On
            if not find_word(sc, "field"):
                press("down*8")
            else:
                press("down*7")
        else:
            # RT on
            if not find_word(sc, "crowd"):
                # RT on, Resolution Scaling on
                if not find_word(sc, "photo"):
                    # DLSS
                    press("down*3")
                else:
                    press("down")

                am.take_screenshot(
                    "3_graphics_rt_scaling.png",
                    ArtifactType.CONFIG_IMAGE,
                    "graphics menu rt when scaling also enabled",
                )
            else:
                # RT on, Resolution Scaling off
                press("down*8")

    else:
        # Normal Run
        press("down*6")

    if not find_word(sc, "shadows"):
        return False

    am.take_screenshot(
        "4_graphics_basic.png", ArtifactType.CONFIG_IMAGE, "graphics basic"
    )

    press("down*10")

    if not find_word(sc, "dynamic"):
        return False

    am.take_screenshot(
        "5_graphics_advanced1.png", ArtifactType.CONFIG_IMAGE, "graphics advanced 1"
    )

    press("down*6")

    if not find_word(sc, "level"):
        return False

    am.take_screenshot(
        "6_graphics_advanced2.png", ArtifactType.CONFIG_IMAGE, "graphics advanced 2"
    )

    press("3")

    if not find_word(sc, "resolution"):
        return False

    # now on video tab
    am.take_screenshot("1_video.png", ArtifactType.CONFIG_IMAGE, "video menu")

    press("b, enter")

    return True
