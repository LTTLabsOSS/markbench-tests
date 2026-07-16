# Harness Utils

Harness Utils contains scripts that are loosely connected around providing helper utilities used across
multiple test harnesses.

## Artifacts

Supplemental artifacts belong in each harness's `run/artifacts/` directory.

MarkBench clears each harness's `run/` directory before every run, so every run starts empty. Harnesses must not perform their own cleanup.

```python
from harness_utils.artifacts import (
    capture_and_save_screenshot,
    copy_artifact,
)
from harness_utils.paths import harness_directories

SCRIPT_DIRECTORY, RUN_DIRECTORY, ARTIFACTS_DIRECTORY = harness_directories(__file__)

copy_artifact("path/to/results.txt", ARTIFACTS_DIRECTORY)
capture_and_save_screenshot(ARTIFACTS_DIRECTORY / "results.png")
```

`report.json` and `harness.log` stay directly in `run/`. No artifact manifest exists.

## OCR Service

`ocr_service.py`

Resolves the OCR `/process` endpoint and searches screenshots for a target word.

### Usage

```python
from harness_utils.ocr_service import find_word, get_ocr_url

url = get_ocr_url()
result = find_word("options", timeout=30, interval=1)
```

`get_ocr_url()` defaults to `http://127.0.0.1:8000/process`. OCR settings from `../../configs/config.toml` relative to this directory take precedence when that file exists; otherwise, `--ocrHost` and `--ocrPort` can override the defaults. The `ip_addr` and `port` arguments provide explicit overrides.

`find_word()` captures a screenshot, posts it with the target word, and retries until it receives a result or the timeout expires. It returns the parsed response data when found, or `None` when no match is found or the request fails. Set `vulkan=True` for Vulkan capture or pass `crop` to limit the captured region.

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
