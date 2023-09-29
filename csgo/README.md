# Counter Strike: Global Offensive

Downloads and installs the [CSGO Benchmark scripts](https://github.com/samisalreadytaken/csgo-benchmark). Runs CS:GO and starts the benchmark. Waits for the benchmark sequence to display the results in the developer console.

## Prerequisites

- Python 3.10+
- Counter Strike: Global Offensive installed.
    - Enable developer console through Settings -> Game -> Enable Developer Console.
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

## Known Issues
When running the test using larger displays / higher resolutions, the Keras service has trouble identifying when the benchmark finishes due to the in-game console not scaling and the text being quite small. The test will then timeout and report as having failed even though the benchmark sequence has successfully completed otherwise.
