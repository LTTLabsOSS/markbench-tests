"""Utility harness for inserting an explicit queue delay."""

import argparse
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delay for a specified number of seconds."
    )
    parser.add_argument("--seconds", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seconds = max(0, args.seconds)
    time.sleep(seconds)


if __name__ == "__main__":
    main()
