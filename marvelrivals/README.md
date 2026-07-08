# Marvel Rivals
This benchmark runs a canned benchmark built into the Marvel Rivals settings.

## Prerequisites

- Python 3.10+
- Marvel Rivals installed on Steam
- OCR service

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `game_version`: number representing the game's current build version
