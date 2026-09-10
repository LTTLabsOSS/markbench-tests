"""Windows utility for clicking the bottom-right corner of a 4K screen."""

import logging
import time

import pydirectinput


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    pydirectinput.FAILSAFE = False
    logging.info("Waiting 5 seconds before clicking at (3839, 2159)")
    time.sleep(5)
    pydirectinput.click(x=3839, y=2159)
    logging.info("Click complete")


if __name__ == "__main__":
    main()
