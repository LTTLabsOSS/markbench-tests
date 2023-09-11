# Forza Horizon 5

## Prerequisites

- Python 3.10+
- Forza Horizon 5 installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Forza Horizon 5 from steam.
      1. Location does not matter, this harness uses Steam command to launch the game.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: forza5
    executable: "forza5.py"
    process_name: "ForzaHorizon5.exe"
    output_dir:
      - 'harness/forza5/run'
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__output_dir__: _(optional)_ Directory containing files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.

## Common Issues
1. "Login to Microsoft" modal pops up
    - This game will not let you pass into the menu if you are not signed into Xbox. If you run this game at least once before running you can login then, or pre-login before running the harness.
