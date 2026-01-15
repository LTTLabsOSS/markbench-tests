import logging

from harness_utils.artifacts import ArtifactManager, ArtifactType
from harness_utils.helper import find_word, int_time, press, sleep


def run_benchmark(am: ArtifactManager) -> tuple[int, int]:
    sleep(15)

    if not navigate_settings(am):
        logging.error("Failed to navigate settings")
        return (0, 0)
        
    logging.info("Starting benchmark")
    
    press("b, enter")
    
    if not find_word("fps", timeout=30):
        return (0, 0)

    test_start_time = int_time() - 3

    logging.info("Benchmark started. Waiting for benchmark to complete.")

    sleep(70)  # make into an editable const, adjust timings

    if not find_word("results", "Did not see results screen."):
        return (0, 0)

    test_end_time = int_time() - 4

    am.take_screenshot(
        "results.png", ArtifactType.RESULTS_IMAGE, "results of benchmark"
    )

    return test_start_time, test_end_time


def navigate_settings(am: ArtifactManager) -> bool:
    """Simulate inputs to navigate the main menu"""

    logging.info("Navigating main menu")

    if not find_word("new", "Did not see main menu.", timeout=30):
        return False

    # navigating to settings menu
    if not find_word("continue"):
        # an account with no save game
        press("left,enter")
    else:
        press("left,down,enter")

    if not find_word("volume", "Did not see settings menu"):
        return False

    # entered settings
    press("3*3")

    if not find_word("preset"):
        return False

    # now on graphics tab

    am.take_screenshot(
        "2_graphics_preset.png", ArtifactType.CONFIG_IMAGE, "graphics preset"
    )

    press("down*2")

    if not find_word("grain"):
        if not find_word("reflections"):
            # RT off
            # Resolution Scaling On
            if not find_word("field"):
                press("down*8")
            else:
                press("down*7")
        else:
            # RT on
            if not find_word("crowd"):
                # RT on, Resolution Scaling on
                if not find_word("photo"):
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

    if not find_word("shadows"):
        return False

    am.take_screenshot(
        "4_graphics_basic.png", ArtifactType.CONFIG_IMAGE, "graphics basic"
    )

    press("down*10")

    if not find_word("dynamic"):
        return False

    am.take_screenshot(
        "5_graphics_advanced1.png", ArtifactType.CONFIG_IMAGE, "graphics advanced 1"
    )

    press("down*6")

    if not find_word("level"):
        return False

    am.take_screenshot(
        "6_graphics_advanced2.png", ArtifactType.CONFIG_IMAGE, "graphics advanced 2"
    )

    press("3")

    if not find_word("resolution"):
        return False

    # now on video tab
    am.take_screenshot("1_video.png", ArtifactType.CONFIG_IMAGE, "video menu")

    return True
