# Cinebench R23 Test Harness

## Prerequisites

- Python 3.10+
- Cinebench R23 installed in `C:\\CinebenchR23\\Cinebench.exe`

> Note: Hopefully it will install itself in the future...

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Unzip Cinebench R23 from https://www.maxon.net/en/downloads into `C:\\CinebenchR23\\Cinebench.exe`

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  name: "cinebenchr23"
  executable: "cinebench.py"
  process_name: "Cinebench.exe"
  asset_paths:
    - "harness/cinebenchr23/run"
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__asset_paths__: _(optional)_ list of files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.


