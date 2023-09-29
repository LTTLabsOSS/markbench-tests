# F1 23

This script navigates through in-game menus to the built in benchmark and runs it with the current settings. It then waits for a results screen, expecting the benchmark to be running 3 laps.

## Prerequisites

- Python 3.10+
- F1 23 installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
