# Horizon Zero Dawn Remastered

Navigates menus to the in-game benchmark then runs it.

## Prerequisites

- Python 3.10+
- Horizon Zero Dawn Remastered installed
- OCR service

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
