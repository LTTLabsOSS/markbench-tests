# Dota 2
Based on the benchmarking guide ["Benchmarking Dota 2" by JJ “PimpmuckL” Liebig](https://medium.com/layerth/benchmarking-dota-2-83c4322b12c0).
The test uses a modified version of the guide's `benchmark.cfg` file originally provided by https://github.com/AveYo/D-OPTIMIZER

## Prerequisites

- Python 3.10+
- Dota 2 installed
- Keras OCR service
- Replay file named `benchmark.dem` copied to harness directory. This is the same file used by the benchmarking guide mentioned above. It can be downloaded [here](https://mega.nz/file/2ZlTiSaZ#byo4nSBjcsP8wsfKQAhFDuOMd0N9flUxtB8QZ4C5tSM)

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds