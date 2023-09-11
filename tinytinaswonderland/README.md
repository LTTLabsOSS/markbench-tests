# Tiny Tina's Wonderland

## Prerequisites

- Python 3.10+
- Tiny Tina's Wonderland installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Tiny Tina's Wonderland from Epic Launcher.
      1. Location **does** matter, the harness has to be aware of install location.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: tinytinaswonderland
    executable: "tinytinaswonderland.py"
    process_name: "Wonderlands.exe"
    output_dir: "run"
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
