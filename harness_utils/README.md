# Harness Utils

Harness Utils contains scripts that are loosely connected around providing helper utilities used across
multiple test harnesses.

## Artifacts

`artifacts.py`

Contains class for capturing test artifacts.

### Usage

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

## OCR Service

`ocr_service.py`

Captures a screenshot and queries the configured OCR HTTP service for a word.

### Usage

```python
from harness_utils.ocr_service import find_word
```

```python
result = find_word("options", timeout=30, interval=1)
result = find_word("continue", timeout=20, interval=1)
result = find_word("options", vulkan=True, timeout=30, interval=1)
```

The default OCR endpoint is `127.0.0.1:8000`. Override it with
`configs/config.toml`:

```toml
[ocr]
host = "127.0.0.1"
port = 8000
```

### Legacy Keras split helper

`keras_service.py`

Only use `KerasService` for harnesses that need `ScreenSplitConfig`.

```python
from harness_utils.keras_service import (
    KerasService,
    ScreenSplitConfig,
    ScreenShotDivideMethod,
    ScreenShotQuadrant,
)
```

```python
ss_config = ScreenSplitConfig(
  divide_method=ScreenShotDivideMethod.HORIZONTAL,
  quadrant=ScreenShotQuadrant.TOP,
)

result = keras_service.wait_for_word(
  "options",
  timeout=30,
  interval=1,
  split_config=ss_config,
)
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
