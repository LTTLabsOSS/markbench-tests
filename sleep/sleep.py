import time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "--seconds",
    dest="seconds",
    help="Time to sleep in seconds",
    required=True,
)
seconds_to_sleep = int(parser.parse_args().seconds)
print(f"Sleeping for {seconds_to_sleep} seconds")
time.sleep(seconds_to_sleep)
