# DOTA 2
Based on the benchmarking guide ["Benchmarking DOTA 2" by JJ “PimpmuckL” Liebig](https://medium.com/layerth/benchmarking-dota-2-83c4322b12c0).
The test uses a modified version of the guide's `benchmark.cfg` file originally provided by https://github.com/AveYo/D-OPTIMIZER.
The benchmark replay we utilize is PlayTime vs Team Falcons DreamLeague Season 29, one of the longest games of the season.

## Prerequisites

- Python 3.10+
- DOTA 2 installed
- OCR service
- Replay file named `8821954344_416769358.dem` copied to harness directory. It can be downloaded [here](https://www.opendota.com/matches/8821954344)

## Options

- `ocrHost`: string representing the IP address of the OCR service. e.x. `0.0.0.0`
- `ocrPort`: string representing the port of the OCR service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds