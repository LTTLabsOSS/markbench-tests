# Shadow of the Tomb Raider

## Prerequisites

- Python 3.10+
- Shadow of the Tomb Raider installed via Steam

## Setup

  1. Follow the setup instructions for the framework.
  2. Install Shadow of the Tomb Raider from steam.

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[heigt]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

## Common Issues
1. "Steam cannot sync with cloud" 
    - A steam modal between test runs (when repeated) will come up.
    - If you are monitoring the test, you can simply manually close the modal and the test should continue normally.
    - The best solution is to disable cloud syncing for all steam games on the test bench.
2. "Image could not be found within timeout"
    - Sometimes running the harness on a new test bench + display combination will not work right away.
    - Try a different template set, or add a new one to recitify this problem.
    - If a new template set isn't working, something else is probably bugging out.
    - This harness won't support resolutions that aren't native aspect ratios to the display.