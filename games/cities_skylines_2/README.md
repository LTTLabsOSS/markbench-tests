# Cities Skylines 2

This benchmark uses a 100,000 population save at a busy intersection to see how the CPU can handle the calculations at 3x speed. It also installs a third party launcher on the system to bypass Paradox's terrible game launcher made by shusaura85. Link available at <https://github.com/shusaura85/notparadoxlauncher>

## Prerequisites

- Python 3.11.*
- Cities Skylines 2 installed
- OCR service
- Bundled `launcher/`, `save/`, and `config/` assets present

On Linux, Steam and Proton, `ydotool`/`ydotoold`, Spectacle, and MangoHud are also required. `ydotoold` must be running, and the invoking user must have access to its socket. The harness launches the game through Steam/Proton and uses Proton-aware launcher, save, and configuration paths.

## Options

- `ocrHost`: string representing the IP address of the OCR service. e.x. `0.0.0.0`
- `ocrPort`: string representing the port of the OCR service. e.x. `8080`

## Output

run/report.json

- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `version`: string representing the game's Steam build ID
