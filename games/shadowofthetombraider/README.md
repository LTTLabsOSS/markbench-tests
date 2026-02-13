# Shadow of the Tomb Raider

This script navigates through the game menus to the built in benchmark and runs it with the current settings. It then waits for a results screen.

## Prerequisites

- Python 3.10+
- Shadow of the Tomb Raider installed via Steam
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

## Common Issues
1. "Steam cannot sync with cloud" 
    - A steam modal between test runs (when repeated) will come up.
    - If you are monitoring the test, you can simply manually close the modal and the test should continue normally.
    - The best solution is to disable cloud syncing for all steam games on the test bench.