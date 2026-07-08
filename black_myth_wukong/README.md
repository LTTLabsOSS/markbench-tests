# Black Myth Wukong

This script navigates the menus of the Black Myth Wukong Benchmark tool and runs it with the current settings. It then waits for a results screen before exiting.

## Prerequisites

- Python 3.10+
- Black Myth Wukong Benchmark Tool installed
- Keras OCR service
- Vgamepad

### Linux vgamepad setup

Linux vgamepad support is experimental and uses `/dev/uinput`. The harness must run without `sudo`; provision `/dev/uinput` access during machine setup, not at benchmark runtime.

For an interactive login session, install a udev rule like:

```udev
KERNEL=="uinput", SUBSYSTEM=="misc", TAG+="uaccess", OPTIONS+="static_node=uinput"
```

For a service or non-seat bench user, prefer a dedicated group provisioned by an administrator:

```udev
KERNEL=="uinput", SUBSYSTEM=="misc", GROUP="uinput", MODE="0660", OPTIONS+="static_node=uinput"
```

Then add the benchmark user to that group during setup. Do not rely on runtime `sudo chmod`; the Python process should be able to open `/dev/uinput` as its normal user before the harness starts.

This only covers the virtual gamepad dependency path. Proton, Steam, and the game install path still need validation on the target Linux bench.

## Options

- `kerasHost`: string representing the IP address of the Keras service. e.x. `0.0.0.0`
- `kerasPort`: string representing the port of the Keras service. e.x. `8080`

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `version` : number representing the build version of the game being tested as reported by steam