# Harness Update Guide

This guide defines how to update an existing harness to follow the standard pattern used by `cyberpunk2077.py`.

The goal is consistency. A harness must have one obvious flow, one OCR/input abstraction, and one place that owns process/report/artifact lifecycle.

## Required Checklist

Use this as the review checklist for an updated harness.

- import `FAILED_RUN`, `find_word`, and `press` from `harness_utils.helper`
- remove `KerasService`, `kerasService`, OCR CLI args, and OCR-specific `ArgumentParser` code
- add `launch_game()` for pre-launch setup and game launch
- flatten navigation helpers into `run_benchmark(am)` unless a helper is a true standalone utility
- make `run_benchmark(am)` return `(start_time, end_time)` or `FAILED_RUN`
- keep logging setup, `ArtifactManager` creation, report generation, manifest creation, teardown, and exit handling in `main()`
- replace keyboard input helpers and button chains with `press(...)`
- use inline `if not find_word(...)` checks when OCR is only a gate
- pass failure logging through `find_word(..., msg=...)` where a timeout message is needed
- use ordered screenshot names like `01_video.png`, `02_graphics_1.png`, `03_graphics_2.png`
- do not pass screenshot descriptions to `take_screenshot(...)`
- ensure no local `FAILED_RUN` constant remains
- ensure no `press_n_times(...)` remains
- ensure no new `user.press(...)` chains remain for keyboard input
- verify with `python -m py_compile path\to\harness.py`

## Target Structure

Use this shape:

- `launch_game()`
- `run_benchmark(am: ArtifactManager) -> tuple[int, int]`
- `main() -> None`

`launch_game()` handles pre-game setup and game launch.

`run_benchmark(am)` handles benchmark navigation, OCR checks, timing, screenshots, and benchmark artifacts created during the run.

`main()` handles logging setup, `ArtifactManager` creation, calling `run_benchmark(am)`, report generation, manifest creation, teardown, and process exit.

## 1. Replace Legacy OCR/Input Usage

Use the shared helper:

```python
from harness_utils.helper import FAILED_RUN, find_word, press
```

Remove legacy OCR/service plumbing:

- `KerasService`
- `kerasService`
- `--kerasHost`
- `--kerasPort`
- `ArgumentParser` code used only for OCR config

Use:

- `find_word(...)` for OCR checks
- `press(...)` for keyboard input sequences

`press(...)` is the standard way to press buttons. Do not add new `user.press(...)` chains or `press_n_times(...)` calls in updated harnesses.

Legacy Keras-specific harness plumbing is being removed. Do not preserve it unless there is a concrete technical blocker.

## 2. Flatten the Navigation Flow

Use one main benchmark function instead of multiple tiny navigation functions that only call each other.

Required:

- `run_benchmark(am)` contains the full benchmark flow in order

Remove:

- `navigate_startup()`
- `offline_menu()`
- `find_graphics()`
- similar one-purpose wrappers unless they contain real reusable logic that is shared

Keep small helpers only when they are genuinely independent utilities, such as file parsing or result-file lookup.

## 3. Add a `launch_game()` Function

Put pre-launch setup here:

- deleting intro videos
- copying mods
- replacing executables
- RTSS or similar launch-adjacent setup if it belongs to game launch
- calling the final game launch command

This keeps `run_benchmark(am)` focused on the actual run.

## 4. Make `run_benchmark(am)` Focused

`run_benchmark(am)` should do these things:

- call `launch_game()`
- navigate menus
- wait for OCR states
- press keys
- take screenshots
- collect run-specific artifacts
- mark benchmark start and end times
- return `(start_time, end_time)`

`run_benchmark(am)` must not own:

- logging setup
- report JSON creation
- manifest creation
- final process termination policy
- final exit code policy

## 5. Use the Failed-Run Tuple Pattern

Use the shared constant from `harness_utils.helper`:

```python
from harness_utils.helper import FAILED_RUN
```

When the harness cannot continue, return `FAILED_RUN` from `run_benchmark(am)` instead of calling `sys.exit(...)` from inside the run flow.

Then in `main()`:

- check whether `(start_time, end_time) == FAILED_RUN`
- set `exit_code = 1` if so

This keeps control flow predictable and matches the newer harness pattern.

## 6. Keep Exit Handling in `main()`

`main()` should follow this pattern:

- `setup_logging(...)`
- create `ArtifactManager`
- initialize `report = None`
- initialize `exit_code = 0`
- call `run_benchmark(am)` inside `try`
- build the report only on success
- in `finally`, create manifest, write report if present, and terminate processes
- `sys.exit(exit_code)` only at the end if needed

This makes cleanup consistent even when the run fails partway through.

## 7. Inline OCR Checks

When OCR is only being used as a gate, do not store it in a temporary variable.

Prefer:

```python
if not find_word("results", timeout=90, interval=3, msg="Did not find results"):
    return FAILED_RUN
```

Avoid:

```python
result = find_word("results", timeout=90, interval=3)
if not result:
    logging.info("Did not find results")
    return FAILED_RUN
```

Only keep the OCR result when coordinates or matched data are actually needed.

## 8. Let `find_word()` Own Timeout Logging

If a failure message is needed, pass it with `msg=...`.

Prefer:

```python
if not find_word("graphics", timeout=15, interval=3, msg="Didn't find graphics"):
    return FAILED_RUN
```

Avoid separate logging immediately before failure when `find_word()` can already do it.

## 9. Use `press()` for All Button Input

Use `press(...)` for all keyboard input in updated harnesses.

Replace repeated or chained keypress logic with a single `press(...)` call.

Examples:

```python
press("down*6")
press("right, enter")
press("space, space, space")
press("up*28, enter")
```

Replace:

- repeated `user.press(...)`
- `press_n_times(...)`

If the old code used a pause close to the helper default, use the helper default instead of preserving tiny timing differences.

Do not introduce new button helpers for keyboard input.

## 10. Standardize Screenshot Naming

Use ordered filenames with numeric prefixes so the artifact list sorts cleanly.

Good:

- `01_video.png`
- `02_graphics_1.png`
- `03_graphics_2.png`
- `04_benchmark.png`
- `05_results.png`

Do not add description text to `take_screenshot(...)`.

Prefer:

```python
am.take_screenshot("01_video.png", ArtifactType.CONFIG_IMAGE)
```

## 11. Verify the File After Refactor

At minimum:

- ensure no stale `KerasService` references remain
- ensure no stale OCR CLI args remain
- ensure no local `FAILED_RUN` redefinition remains
- ensure no `press_n_times(...)` remains
- ensure no new `user.press(...)` chains remain for keyboard input
- ensure `run_benchmark(am)` returns a tuple on all failure paths
- run:

```powershell
python -m py_compile path\to\harness.py
```

## Working Standard

When updating a harness, optimize for:

- one clear execution flow
- one shared OCR/input abstraction
- consistent artifact naming
- predictable cleanup
- minimal boilerplate

If a harness still needs special behavior, keep it. Otherwise, follow the shared pattern directly. The update work is intended to remove legacy harness variation, not preserve it.
