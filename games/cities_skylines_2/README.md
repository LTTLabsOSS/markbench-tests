# Cities Skylines 2
This benchmark uses a 100,000 population save at a busy intersection to see how the CPU can handle the calculations at 3x speed. It also installs a third party launcher on the system to bypass Paradox's terrible game launcher made by shusaura85. Link available at https://github.com/shusaura85/notparadoxlauncher

## Prerequisites

- Python 3.10+
- Cities Skylines 2 installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds