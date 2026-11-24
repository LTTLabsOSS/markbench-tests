# MarkBench Test Harnesses

Harnesses that run through Markbench

Can also be run as standalone scripts

## Harnesses

Harness categories:

- `games/`
- `non_games/`
- `stress/`
- `utility/`

Basic Harness Files:

- TOML descriptor
- Python entry point specified by the TOML's `py_script` field

The TOML contains orchestration metadata. 

The Python entry point handles:

- Launch and setup
- UI automation
- Benchmark timing
- Artifact capture
- Report writing
- Cleanup
- Exit status

## Generic harness TOML example

```toml
friendly_name = "Example Game"
category = "game"
ocr = false
save_run = true
py_script = "run.py"
executable = "game.exe"
presentmon_enabled = true
presentmon_terminate_on_proc_exit = false
presentmon_delay = 0

[[args]]
name = "quality"
type = "select"
values = ["Low", "High"]
default = "High"
tooltip = "Graphics quality"
```


`[[args]]` is optional and repeatable.

Option types:

- `select`: uses `values`
- `input`: accepts free-form text
- `tooltip`: optional help text
- `default`: optional default for the field

## Outputs

Outputs live under each harness's `run/` directory:

- `run/harness.log`
  - Execution log
- `run/report.json`
  - Machine-readable result
- `run/artifacts/`
  - Screenshots
  - Copied files
  - `artifacts.yaml`

Common `run/report.json` fields:

- `resolution`: `WIDTHxHEIGHT`
- `start_time`: epoch milliseconds
- `end_time`: epoch milliseconds
- `version`: game or benchmark version
- `score`: benchmark result when applicable
- `unit`: score unit when applicable

## NOTES

- Name of Harness folder and name of harness TOML file *MUST* match to work with Markbench