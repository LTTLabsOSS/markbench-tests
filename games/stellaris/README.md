# Stellaris

This benchmark uses vanilla Stellaris (No DLC) and the popular [console command](https://stellaris.paradoxwikis.com/Console_commands): one_year. We created a save game:

- 30 advanced start AI empires
- Max saturation of hyperlanes
- Maximum galaxy size

We used the fast_forward command to get to year 2400.

## Prerequisites

- Python 3.10+
- Stellaris installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `score` number of seconds to advance one full year in game