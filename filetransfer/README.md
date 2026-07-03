# File Transfer Test Harness

Downloads test video from the L:/ drive to an indicated source drive, them transfers said file to your destination drive while recording hwinfo.

## Prerequisites

- Python 3.10+
- Connection to L: drive

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `score` : write speeds averaged over the test
- `read_score` : read speeds averaged over the test
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds