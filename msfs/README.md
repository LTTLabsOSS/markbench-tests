# Microsoft Flight Simulator 2020

This script loads a flight plan that has a Bonanza G36 fly from the Boundary Bay Airport, over the Labs Building and landing at the Pitt Meadows Regional Airport. This benchmark requires a mod made by hoghimet5. Download it at https://www.nexusmods.com/microsoftflightsimulator/mods/647?tab=description

## Prerequisites

- Python 3.10+
- Microsoft Flight Simulator installed
- Bonanza Turbo V4.1 Folder copied to the Markbench harness
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds