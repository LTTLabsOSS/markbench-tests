# Forza Motorsport

This script navigates through in-game menus to the built in benchmark and runs it with the current settings. The script runs for 3 minutes after the benchmark results come up to get a longer average as the game keeps running after the benchmark.

## Prerequisites

- Python 3.10+
- Forza Motorsport via Steam
- Keras OCR service

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

## Common Issues
1. "Login to Microsoft" modal pops up
    - This game will not let you pass into the menu if you are not signed into Xbox. If you run this game at least once before running you can login then, or pre-login before running the harness.
