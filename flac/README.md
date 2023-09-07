# FurMark Test Harness

## Prerequisites

- Python 3.10+
- FurMark installed and on path.

This harness expects that FurMark has been installed on the system using installer defaults.
> Note: Hopefully it will install itself in the future if not present.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install FurMark from https://geeks3d.com/furmark/downloads/
      1. Follow the installer's defaults.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: furmark
    executable: "furmark.py"
    process_name: "FurMark.exe"
    asset_paths:
      - 'C:\Program Files (x86)\Geeks3D\Benchmarks\FurMark\furmark-gpu-monitoring.xml'
      - 'C:\Program Files (x86)\Geeks3D\Benchmarks\FurMark\FurMark_0001.txt'
      - 'C:\Program Files (x86)\Geeks3D\Benchmarks\FurMark\furmark-gpu-monitoring.csv'
    args:
      - "/nogui"
      - "/nomenubar"
      - "/noscore"
      - "/width=640"
      - "/height=480"
      - "/msaa=4"
      - "/run_mode=1"
      - "/max_time=10000"
      - "/log_temperature"
      - "/disable_catalyst_warning"
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__asset_paths__: _(optional)_ list of files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.

__args__ : _(optional)_ list of arguments to be appended to the command to execute. All the arguments will be passed to
the executable when invoked by the framework.

Arguments for this harness are the same
as [the documented CLI arguments](https://www.geeks3d.com/20081123/geeks3d-howto-know-furmarks-command-line-parameters/)
.

