# Dota 2
Follows the benchmarking guide ["Benchmarking Dota 2" by JJ “PimpmuckL” Liebig](https://medium.com/layerth/benchmarking-dota-2-83c4322b12c0)

## Prerequisites

- Python 3.10+
- Dota 2 installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds