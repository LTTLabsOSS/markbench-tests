from argparse import ArgumentParser
import os

# Stub


def get_resolution() -> tuple[int]:
    return 0, 0


def get_args() -> any:
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()


def remove_intro_videos(file_paths: list[str]) -> None:
    for video in file_paths:
        try:
            os.remove(video)
        except FileNotFoundError:
            # If file not found, it has likely already been deleted before.
            pass
