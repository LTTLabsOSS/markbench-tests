# Harness Utils

Harness Utils contains scripts that are loosely connected around providing helper utilities used across
multiple test harnesses.

## Artifacts

`artifacts.py`

Contains class for capturing test artifacts.

### Usage:

Import `ArtifactManager` and `ArtifactType`

```
from harness_utils.artifacts import ArtifactManager, ArtifactType
```

Instantiate an Artifact Manager; This should ideally be the same directory as specified for the output directory of the harness, e.g. `./run`.

```python
# Assuming /run is used, get output directory relative to script location.
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR.joinpath("run")

am = ArtifactManager(LOG_DIR)
```

Capture artifacts using `ArtifactManager.copy_file` and `ArtifactManager.take_screenshot`.

```python
# src as a string, capturing a configuration text file
am.copy_file("path/to/config.ini", ArtifactType.CONFIG_TEXT, "a config file")

# src as a pathlib.Path, capturing a results text file
am.copy_file(Path("path", "to", "results.txt"), ArtifactType.RESULTS_TEXT, "some results")

am.take_screenshot("cool_picture.png", ArtifactType.CONFIG_IMAGE, "picture of settings")
```

Optionally, an override to the screenshot function can optionally be provided if the `mss` library is not sufficient.

```python
def my_screenshot_function(filename: str) -> None:
    # Take the screenshot here using the filename
    pass

am.take_screenshot("something.png", ArtifactType.CONFIG_IMAGE, "a picture taken with my function", my_screenshot_function)
```

Once all desired artifacts have been captured, create an artifact manifest with `ArtifactManager.create_manifest`.

```python
am.create_manifest()
```

Given the configuration and artifacts captured in the above code snippets, the resulting manifest should be created at `./run/artifacts.yaml` and contain the following data:

```yaml
- filename: config.ini
  type: config_text
  description: a config file
- filename: results.txt
  type: results_text
  description: some results
- filename: cool_picture.png
  type: config_image
  description: picture of settings
- filename: something.png
  type: config_image
  description: a picture taken with my function
```

## Keras Service

`keras_service.py`

Contains class for instancing connection to a Keras Service and provides access to its web API.

### Usage:

Import KerasService

```python
from harness_utils.keras_service import KerasService
```

Instantiate a Keras

```python
# usually your host and port will come from the script arguments
keras_service = KerasService(args.keras_host, args.keras_port)
```

You can look a word on the screen for a number of attempts, or wait for a word to appear on the screen for an amount of time.

```python
# this will send a screenshot every 1 second to keras and look for the word "options" in it
# this function call will block until the word has been found returning True, or None once 30 seconds has passed
result = keras_service.wait_for_word("options", timeout=30, interval=1)

# this will send a screenshot to keras every 1 second ato keras and look for the word "continue" in it
# this function call will block until it has tried 20 times
result = keras_service.look_for_word("continue", attempts=20, interval=1)
```

You can optionally check only half the screen, or 1/4 of the screen. This shrinks the amount of screenshot that Keras has to search for a word which means a faster result time.

First import ScreenSplitConfig, ScreenShotDivideMethod, and ScreenShotQuadrant

```python
from harness_utils.keras_service import KerasService, ScreenSplitConfig, ScreenShotDivideMethod, ScreenShotQuadrant
```

Then create your ScreenSplitConfig object and pass it to the look_for_word or wait_for_word functions.

```python
# this config will split the screen horizontally and look in the top of the screen
ss_config = ScreenSplitConfig(
  divide_method=ScreenShotDivideMethod.HORIZONTAL
  quadrant=ScreenShotQuadrant.TOP
)

# this one will split the screen vertically and look in the right of the screen
ss_config = ScreenSplitConfig(
  divide_method=ScreenShotDivideMethod.VERTICAL
  quadrant=ScreenShotQuadrant.RIGHT
)

# ans this will split the screen into 4 and look in the bottom left of the screen
ss_config = ScreenSplitConfig(
  divide_method=ScreenShotDivideMethod.QUADRANT
  quadrant=ScreenShotQuadrant.BOTTOM_LEFT
)

# pass the config to the function call
result = keras_service.wait_for_word("options", timeout=30, interval=1, split_config=ss_config)
```

## Output

`output.py`

Functions related to logging and formatting output from test harnesses.

## Misc

`misc.py`

Misc utility functions

## Process

`process.py`

Functions related to managing processes.

## RTSS

`rtss.py`

Functions related to setting up and using RTSS configs.

## Steam

`steam.py`

Functions related to using Steam for running games