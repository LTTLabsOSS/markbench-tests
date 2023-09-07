# Red Dead Redemption 2

## Prerequisites

- Python 3.10+
- Red Dead Redemp installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Red Dead Redemption 2 from steam.
      1. Location does not matter, this harness uses steam to launch the game.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: reddeadredemption2
    executable: "reddeadredemption2.py"
    process_name: "RDR2.exe"
    asset_paths:
      - 'harness/reddeadredemption2/run'
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__asset_paths__: _(optional)_ list of files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.

__args__ : _(optional)_ list of arguments to be appended to the command to execute. All the arguments will be passed to
the executable when invoked by the framework.

### Arguments

## Common Issues

