# Microsoft Flight Simulator

## Prerequisites

- Python 3.10+
- Microsoft Flight Simulator installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Microsoft Flight Simulator from steam or Microsoft Store
      1. Location does not matter, this harness uses Windows App Store command to launch the game.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: msflightsimulator
    executable: "msflightsimulator.py"
    process_name: "FlightSimulator.exe"
    asset_paths:
      - 'harness/msflightsimulator/run'
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__asset_paths__: _(optional)_ list of files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.

## Common Issues

