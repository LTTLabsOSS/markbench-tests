# Marvel Rivals
This benchmark runs a replay of a Season 1 tournament Double Elimination round game between SendHelp and BeerLovers

## Prerequisites

- Python 3.10+
- Marvel Rivals installed on Epic Games
- Keras OCR service
- Favoriting replay ID 10518740076

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `game_version`: number representing the game's current build version