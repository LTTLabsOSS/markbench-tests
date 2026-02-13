# Black Myth Wukong

This script navigates the menus of the Black Myth Wukong Benchmark tool and runs it with the current settings. It then waits for a results screen before exiting.

## Prerequisites

- Python 3.10+
- Black Myth Wukong Benchmark Tool installed
- Keras OCR service
- Vgamepad

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0`
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `version` : number representing the build version of the game being tested as reported by steam