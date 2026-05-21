# Linux Platform Helper Port

## Status

- Branch: `feature/linux-platform-helpers-cyberpunk`
- Synced base commit: `f4fd593`
- Scope: Cyberpunk first, with helpers reusable repo-wide.
- Linux backend choice: `ydotool`
- Linux Steam contract: native Steam, one configured library, `$STEAM_DIR` preferred with `~/.local/share/Steam` fallback.
- Overall status: Phase 12 complete.

## Phase 1: Branch And Baseline

- Status: Complete.
- Changed files:
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `git status --short`: `?? LINUX_PORTING_PLAN.md`
- Caveats/follow-up:
  - No push planned.

## Phase 2: Platform Detection

- Status: Complete.
- Changed files:
  - `harness_utils/platform.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
- Caveats/follow-up:
  - `python` is not available on PATH in this shell; used the working `uv` Python runner.

## Phase 3: Steam Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/steam.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
- Caveats/follow-up:
  - Linux launch requires native `steam` on PATH.
  - Linux helper assumes one controlled Steam library and does not parse `libraryfolders.vdf` or support Flatpak Steam.

## Phase 4: Proton And Windows Path Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/paths.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
- Caveats/follow-up:
  - Linux Windows-path helpers require a valid Steam app ID and existing Proton prefix paths.

## Phase 5: Input Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/input.py`
  - `harness_utils/misc.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
  - `uv run --no-sync python -c "import harness_utils.misc; print('misc import ok')"`: passed after lazy optional imports.
  - `uv run --no-sync python -c "from harness_utils.misc import LTTGamePad360; LTTGamePad360().single_press(); print('gamepad noop ok')"`: passed.
- Caveats/follow-up:
  - Linux input requires the system `ydotool` command and currently maps the Cyberpunk keys only.
  - Missing `vgamepad` is ignored with no-op gamepad methods until a Linux replacement is chosen.

## Phase 6: Screenshot Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/artifacts.py`
  - `harness_utils/keras_service.py`
  - `harness_utils/screenshot.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils cyberpunk2077`: passed after unit test removal.
- Caveats/follow-up:
  - Wayland/wlroots screenshot capture uses system `grim`.
  - X11 screenshot capture falls back to `mss`.

## Phase 7: Process Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/process.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
- Caveats/follow-up:
  - Substring matching remains a fallback for compatibility with existing harness behavior.

## Phase 8: Asset Helpers

- Status: Complete.
- Changed files:
  - `harness_utils/assets.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils`: passed.
- Caveats/follow-up:
  - Cyberpunk assets can be supplied with `MARKBENCH_CYBERPUNK_ASSET_DIR`; Linux does not assume UNC access.

## Phase 9: Cyberpunk Migration

- Status: Complete.
- Changed files:
  - `cyberpunk2077/cyberpunk2077.py`
  - `cyberpunk2077/cyberpunk_utils.py`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall cyberpunk2077 harness_utils`: passed.
- Caveats/follow-up:
  - Cyberpunk runtime validation remains pending on both Windows and Linux.

## Phase 10: Dependency Split

- Status: Complete.
- Changed files:
  - `pyproject.toml`
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils cyberpunk2077`: passed.
- Caveats/follow-up:
  - Linux system dependencies `ydotool` and `grim` are documented in the Linux optional dependency section.

## Phase 11: Tests

- Status: Removed by request.
- Changed files:
  - `LINUX_PORTING_PLAN.md`
- Test command/result:
  - `uv run --no-sync python -m compileall harness_utils cyberpunk2077`: passed.
- Caveats/follow-up:
  - Used `uv run --no-sync python` because `python` is not available on PATH in this shell.
  - All branch-added unittest files were removed by request.

## Phase 12: Manual Validation Notes

- Status: Complete.
- Changed files:
  - `LINUX_PORTING_PLAN.md`
  - `harness_utils/misc.py`
  - `harness_utils/steam.py`
  - `harness_utils/artifacts.py`
  - `harness_utils/keras_service.py`
  - `harness_utils/screenshot.py`
  - `pyproject.toml`
- Test command/result:
  - `git status --short`: clean after removing the untracked `uv.lock` generated by `uv run`.
  - `git log --oneline --decorate -14`: showed the requested phase commits from `docs: track Linux platform helper port` through `docs: record Linux helper validation notes`, plus `fix: keep misc helpers importable without gamepad deps`, based on `f4fd593`.
  - `uv run --no-sync python -m compileall harness_utils cyberpunk2077`: passed.
  - `uv run --no-sync python -c "import harness_utils.misc; print('misc import ok')"`: passed.
  - `uv run --no-sync python -c "from harness_utils.misc import LTTGamePad360; LTTGamePad360().single_press(); print('gamepad noop ok')"`: passed.
- Manual validation:
  - Windows manual Cyberpunk run: pending.
  - Linux manual Cyberpunk run: pending.
- Known remaining scripts not migrated:
  - Non-Cyberpunk benchmarks remain on their existing Windows-specific input/path/registry patterns.
  - Examples include direct `pydirectinput` imports, hard-coded `C:\` paths, `LOCALAPPDATA`/`APPDATA` lookups, and direct `winreg` imports outside the new helpers.
- Caveats/follow-up:
  - `python` is not available on PATH in this shell; validation used `uv run --no-sync python`.
  - Linux runtime requires Steam/Proton, `ydotool`, and either X11 screenshot access or Wayland/wlroots `grim`.
  - Linux Steam runtime assumes native Steam, one library, and `STEAM_DIR` or `~/.local/share/Steam`.
