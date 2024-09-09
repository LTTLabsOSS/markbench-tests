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
am.copy_file("path/to/config.ini", ArtifactType.TEXT_CONFIG, "a config file")

# src as a pathlib.Path, capturing a results text file
am.copy_file(Path("path", "to", "results.txt"), ArtifactType.TEXT_RESULTS, "some results")

am.take_screenshot("cool_picture.png", ArtifactType.IMAGE_CONFIG, "picture of settings")
```

Once all desired artifacts have been captured, create an artifact manifest with `ArtifactManager.create_manifest`.

```python

am.create_manifest()
```

Given the configuration and artifacts captured in the above code snippets, the resulting manifest should be created at `./run/artifacts.yaml` and contain the following data:

```yaml
- filename: config.ini
  type: text_config
  description: a config file
- filename: results.txt
  type: text_results
  description: some results
- filename: cool_picture.png
  type: image_config
  description: picture of settings
```

## Keras Service

`keras_service.py`

Contains class for instancing connection to a Keras Service and provides access to its web API.

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