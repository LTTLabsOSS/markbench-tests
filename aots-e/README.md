# Ashes of the Singularity - Escalation

This benchmark runs one of the built in benchmarks for the game.

## Prerequisites

- Python 3.10+
- Stellaris installed
- Keras OCR service

## Options

- `benchmark`: Specifies which benchmark to run

## Output

report.json
- `test`: The name of the selected benchmark
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `score` : average fps for the benchmark
- `version` : The build number of the game according to steam