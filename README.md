# MarkBench Test Harnesses

This repository contains benchmark harnesses used with MarkBench. MarkBench can discover and orchestrate their TOML descriptors, but each Python entry point can also be run directly.

## Requirements and setup

The project requires Python `==3.11.*` and uses `uv` for dependency management. Each harness may also require its benchmark or game, OCR service, mods, configuration, or other local assets.

### Windows

1. Install Git, `uv`, and Python 3.11.
2. Clone the repository and install its dependencies from PowerShell:

   ```powershell
   git clone https://github.com/LTTLabsOSS/markbench-tests.git
   cd markbench-tests
   uv sync
   ```

3. Install and prepare the game and assets required by the chosen harness.
4. Run its Python entry point from the repository root, replacing the sample path with the actual harness path:

   ```powershell
   uv run python games/example_game/example_game.py
   ```

## Harness layout and lifecycle

Harnesses are grouped under `games/`, `non_games/`, `stress/`, and `utility/`. A game harness directory normally pairs a TOML descriptor with the Python file named by its `py_script` field.

The TOML is orchestration metadata. The Python entry point owns the applicable lifecycle: launch and setup, UI automation, benchmark timing, artifact capture, report writing, cleanup, and success or failure exit handling.

## Generic game harness example

This example includes every currently used game metadata field and both supported option types:

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

`[[args]]` is optional and repeatable. A `select` option uses `values`; an `input` option accepts a free-form value. `tooltip`, `default`, and `presentmon_ignore_exit` are optional.

## Writing input automation

Prefer the shared sequence helper for key presses. It accepts comma-separated steps, `*N` repeats, and a pause between presses:

```python
from harness_utils.input import press

press("left, down, enter")
press("down*3", pause=5)
```

Use the shared `user` object only for actions that `press` cannot express, such as holds, hotkeys, clicks, mouse movement, or scrolling.

## Outputs

Outputs live under each harness's `run/` directory:

- `run/harness.log` — execution log
- `run/report.json` — machine-readable result
- `run/artifacts/` — screenshots, copied configuration, and artifact metadata

Game reports commonly provide resolution and millisecond `start_time`/`end_time` markers that bound FPS measurement. Non-game reports commonly provide scalar scores and units.

## Linux

Linux support is per harness, not repository-wide. Verify the chosen harness and its dependencies on your Linux setup before attempting a run.

Depending on the harness, a Linux bench may need Steam and Proton, `ydotool` with `ydotoold`, Spectacle, the OCR service, and MangoHud. Ensure `ydotoold` is running and the invoking user has permission to access its input socket. Provision `/dev/uinput` access only for harnesses requiring virtual gamepad input.

Contributors should use the shared helpers in `harness_utils.input`, `harness_utils.steam`, `harness_utils.screenshot`, and `harness_utils.paths` for input, Steam launch/discovery, screenshots, and Proton-aware paths.





## License and contributions

Distributed under the [GNU General Public License v3](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) and [GitHub Issues](https://github.com/LTTLabsOSS/markbench-tests/issues) for contribution and issue-reporting guidance.
