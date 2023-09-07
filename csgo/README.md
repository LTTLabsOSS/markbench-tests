# Shadow of the Tomb Raider

## TODO's
- Iteration within the same game process.
- Accept resolution as a separate argument to the harness.

## Prerequisites

- Python 3.10+
- Counter Strike: Global Offensive installed.
    - Developer console enabled.
    - Benchmark script installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install CSGO from steam.
      1. Location does not matter, this harness uses steam to launch the game.
  3. Enable developer console through Settings -> Game -> Enable Developer Console.
  4. Install bench mark script.
      1. Download the code from https://github.com/samisalreadytaken/csgo-benchmark. *[Code -> Download Code](https://github.com/samisalreadytaken/csgo-benchmark/archive/master.zip)*
      2. Extract contents of zip.
      3. Merge the /csgo/ folder with your /steamapps/common/Counter-Strike Global Offensive/csgo/ folder.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: csgo
    executable: "csgo.py"
    process_name: "csgo"
    output_dir:
      - 'harness/csgo/run'
    args:
      - ""
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__output_dir__: _(optional)_ Directory containing files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.

__args__ : _(optional)_ list of arguments to be appended to the command to execute. All the arguments will be passed to
the executable when invoked by the framework.

### Arguments
|flag|required|what?|notes
|--|--|--|--|
|N/A|N/A|N/A|N/A|

Currently this harness is very basic and does not accept any arguments, it simply launches the game and executes the benchmark. It will use current display and graphics settings.

## Common Issues

