# Rocket League

This test launches a replay of Rocket League. The replay is from RLCS Season 9 NA Playoffs Series 4 [game of NRG vs G2](https://ballchasing.com/replay/bd63746b-cbe7-4d29-8f84-c8da3c4c1703?g=series-4-g2-esports-4-3-nrg-espo-qe6nf31lzt).

## Prerequisites

- Python 3.10+
- Rocket League installed
- Keras OCR service
- Vgamepad

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `game_version`: number representing the game's current build version