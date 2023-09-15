# F1 23

## Prerequisites

- Python 3.10+
- F1 23 installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras serivce. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[heigt]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds