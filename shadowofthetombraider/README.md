# Shadow of the Tomb Raider

## TODO's
- Iteration within the same game process.
- Accept resolution as a separate argument to the harness.

## Prerequisites

- Python 3.10+
- Shadow of the Tomb Raider installed.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Shadow of the Tomb Raider from steam.
      1. Location does not matter, this harness uses steam to launch the game.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: shadowofthetombraider
    executable: "shadowofthetombraider.py"
    process_name: "SOTTR.exe"
    asset_paths:
      - 'harness/shadowofthetombraider/run'
    args:
      - "--preset medium"
      - "--resolution 1920,1080
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
|flag|required|what?|notes
|--|--|--|--|
|--preset|No|Graphics preset to load for test|See the `presets` folder to determine options. If none provided, the current settings will be used|
|--resolution|No|Display settings to load for test|If none provided, current display settings will be used|

#### Presets
This harness requires a single argument for the option `preset`. This is the graphics presets that are found in the game. They are represented in YAML in the folder **presets**. To select one you take the prefix of the name of the file, and the harness will find the corresponding YAML file.

For example if I pass in the argument `--preset medium` to the harness. The harness will load the settings in `presets/medium.presets.yaml`. You can also create and supply a custom preset if you wish.

#### Resolution
Resolution is expected to be givin in the format `height,width` so for example `1920,1080`. An error will be thrown if that format is not provided.

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