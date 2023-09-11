# Assassins Creed Valhalla

## TODO's
- Iteration within the same game process.

## Prerequisites

- Python 3.10+
- Assassins Creed Valhalla installed

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install Assassins Creed Valhalla from Ubisoft.
      1. Location should be default C:\ path

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: acvalhalla
    executable: "acvalhalla.py"
    output_dir:
      - 'harness/acvalhalla/run'
    args:
      - "--preset medium"
      - "--resolution 1080,1920"
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
|--preset|No|Graphics preset to load for test|See the `presets` folder to determine options. If none provided, the current settings will be used|
|--resolution|No|Display settings to load for test|If none provided, current display settings will be used|
|--template_set|No|Template set of images to use. Thesse are what are used to find buttons on the screen|If not provided 1080 set is default|

#### Presets
This harness requires a single argument for the option `preset`. This is the graphics presets that are found in the game. They are represented in YAML in the folder **presets**. To select one you take the prefix of the name of the file, and the harness will find the corresponding INI file.

For example if I pass in the argument `--preset medium` to the harness. The harness will load the settings in `presets/medium.ini`. You can also create and supply a custom preset if you wish.

#### Resolution
Resolution is expected to be passed in as `<height>,<width>`. 

#### Template Set
This harness uses OpenCV template matching to click on buttons through the menu. Sometimes the template matching can be finicky and not find images. Trying out different template sets can sometimes alleviate this issue. Or adding a template set for a specific display and test bench combination.

You can see what options there are in `images` folder. Each set is in a labelled folder.

> Yes, finding buttons on the screen via features or text search would be better, but this is one of the first harnesses, and brute forcing was easiest option.. cut me some slack.

## Common Issues

