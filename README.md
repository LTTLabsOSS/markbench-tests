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

This example includes all current fields and option types:

```toml
friendly_name = "Example Game"
py_script = "example_game.py"
executable = "ExampleGame.exe"
presentmon_enabled = true
presentmon_ignore_exit = true
category = "game"
ocr = true

[[args]]
name = "benchmark"
type = "select"
tooltip = "Choose the benchmark scene"
values = ["battle", "campaign"]
default = "battle"

[[args]]
name = "duration_seconds"
type = "input"
tooltip = "Benchmark duration in seconds"
default = "120"
```

`presentmon_ignore_exit` is an optional field, defaults to FALSE.

`[[args]]` is optional and repeatable.

Option types:

- `select`: uses `values`
- `input`: accepts free-form text
- `tooltip`: optional help text
- `default`: optional default for the field

- `presentmon_ignore_exit`

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