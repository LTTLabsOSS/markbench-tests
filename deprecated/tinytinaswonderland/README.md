# Tiny Tina's Wonderland

This script navigates through in-game menus to the built in benchmark and runs it with the current settings.

## Prerequisites

- Python 3.10+
- Tiny Tina's Wonderland installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Tiny Tina's Wonderland from Epic Launcher.
      1. Location **does** matter, the harness has to be aware of install location.

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

## Known Issues
1. "Login to Microsoft" modal pops up
    - This game will not let you pass into the menu if you are not signed into Xbox. If you run this game at least once before running you can login then, or pre-login before running the harness.
