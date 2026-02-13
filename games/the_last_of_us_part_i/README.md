# The Last of Us Part I

This script loads the game at a specific checkpoint then waits for the scene to play out before quitting the game.

## Prerequisites

- Python 3.10+
- The Last of Us Part I installed
- Keras OCR service

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0` 
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Test Setup

After initial installation of the game or after an update has been installed, the game will typically display a warning about building shaders. Allow the game to finish building shaders before running the test harness, as running the harness before this process is complete can negatively impact performance of the game and the reliability of the harness.

<img src="images/Shader Warning.jpg" alt="Shader Warning" width="960" />

*The shader warning as seen in game.*

The test harness expects to be running from a specific checkpoint in the game, namely the *Hometown - Prologue* checkpoint. As such a save file needs to be present as the last item in the list for the harness to navigate the menus correctly and load into the correct point in the game.

<img src="images/Load Game Menu.jpg" alt="Load Game Menu" width="960"  />

*The necessary checkpoint for the harness to run.*


## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds