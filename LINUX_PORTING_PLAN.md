# Linux Platform Helper Port

## Status

- Branch: `feature/linux-platform-helpers-cyberpunk`
- Synced base commit: `f4fd593`
- Scope: Cyberpunk first, with helpers reusable repo-wide.
- Linux backend choice: `ydotool`
- Overall status: Phase 3 complete.

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
  - Linux launch requires `steam` or `flatpak` on PATH.

## Phase 4: Proton And Windows Path Helpers

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 5: Input Helpers

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 6: Screenshot Helpers

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 7: Process Helpers

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 8: Asset Helpers

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 9: Cyberpunk Migration

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 10: Dependency Split

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 11: Tests

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.

## Phase 12: Manual Validation Notes

- Status: Pending.
- Changed files: Pending.
- Test command/result: Pending.
- Caveats/follow-up: Pending.
