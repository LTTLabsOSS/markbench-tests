# Harness Update Candidates

This document tracks the remaining game harnesses that are good candidates for migration to the current harness standard.

The categories below are intended to help choose the next files to update. They are based on expected migration complexity, not on benchmark importance.

## Usage Priority

The following harnesses are the most used and should be treated as high-priority migration targets:

- `alanwake2/alanwake2.py`
- `the_last_of_us_part_i/the_last_of_us_part_i.py`
- `black_myth_wukong/blackmythwukong.py`
- `doomdarkages/doomdarkages.py`
- `reddeadredemption2/reddeadredemption2.py`

This priority does not change their complexity classification. It does change planning. A high-use harness in a harder category may still deserve earlier attention than a low-risk harness in the `Easy` group.

## Classification Rules

- `Easy`: standard keyboard/OCR harnesses with no major structural blockers
- `Medium`: still suitable for migration, but with extra setup, save handling, or config handling that needs care
- `Special-Case`: updateable, but the harness has a non-standard control path or a more fragile runtime model

## Easy Candidates

These harnesses should map cleanly to the standard update pattern in `HARNESS_UPDATE_GUIDE.md`.

- `acshadows/acshadows.py`
- `atomic_heart/atomic_heart.py`
- `farcry6/farcry6.py`
- `forza5/forza5.py`
- `forzamotorsport/forzams.py`
- `grid_legends/grid_legends.py`
- `horizonzdr/hzdr.py`
- `tinytinaswonderland/tinytinaswonderland.py`
- `total_war_pharaoh/twp.py`
- `total_war_warhammer_iii/twwh3.py`

Why these are in `Easy`:

- they are primarily keyboard plus OCR harnesses
- they do not depend on split-screen OCR
- they do not depend on screenshot photo matching
- their quirks fit naturally into the updated structure

Typical quirks in this group:

- intro-video removal before launch
- RTSS startup and teardown
- config or results file copying after the run
- mouse scrolling inside settings menus

These quirks do not change the migration approach. They only affect what belongs in `launch_game()` and what belongs in `run_benchmark(am)`.

## Medium Candidates

These harnesses are still good migration targets, but they require more care when placing setup and cleanup responsibilities.

- `alanwake2/alanwake2.py`
- `returnal/returnal.py`
- `stellaris/stellaris.py`
- `the_last_of_us_part_i/the_last_of_us_part_i.py`
- `the_last_of_us_part_ii/tlou2.py`

Why these are in `Medium`:

- they still fit the update pattern overall
- they have extra pre-run state management that is easy to misplace during refactor
- they are more likely to mix benchmark flow with environment preparation

Typical quirks in this group:

- save copying from network or local staging
- autosave reset logic
- registry-backed settings or resolution lookup
- more involved launch preparation than a simple process start

The main risk here is not OCR conversion. The main risk is incorrectly moving save/setup logic into the wrong layer.

High-use harnesses in this group:

- `alanwake2/alanwake2.py`
- `the_last_of_us_part_i/the_last_of_us_part_i.py`

## Special-Case Candidates

These harnesses can still be updated, but they should not be treated like routine keyboard/OCR migrations.

- `aots-e/aotse.py`
- `black_myth_wukong/blackmythwukong.py`
- `doomdarkages/doomdarkages.py`
- `reddeadredemption2/reddeadredemption2.py`
- `rocket_league/rocket_league.py`

Why these are in `Special-Case`:

- they contain behavior that changes the migration strategy
- the standard refactor still applies conceptually, but not mechanically

File-specific notes:

- `aots-e/aotse.py`
  Uses executable replacement and restoration. Cleanup behavior matters more than usual.

- `black_myth_wukong/blackmythwukong.py`
  Uses Xbox gamepad input. This is not a normal `press(...)` keyboard migration.

- `doomdarkages/doomdarkages.py`
  Uses Vulkan OCR and heavy menu scrolling. OCR conversion needs the Vulkan path preserved.

- `reddeadredemption2/reddeadredemption2.py`
  Uses Vulkan OCR throughout. This is a helper migration, but not a basic one.

- `rocket_league/rocket_league.py`
  Uses DS4 gamepad input. Like Wukong, this is not a normal keyboard harness.

High-use harnesses in this group:

- `black_myth_wukong/blackmythwukong.py`
- `doomdarkages/doomdarkages.py`
- `reddeadredemption2/reddeadredemption2.py`

## Recommended Next Targets

If the goal is to make progress quickly while validating the migration pattern across a few different harness shapes, start with:

1. `acshadows/acshadows.py`
2. `grid_legends/grid_legends.py`
3. `forzamotorsport/forzams.py`
4. `forza5/forza5.py`
5. `farcry6/farcry6.py`

Why these should go first:

- they are representative enough to validate the pattern
- they avoid the biggest edge cases
- they should produce useful follow-up adjustments to the guide without forcing gamepad or Vulkan-specific work immediately

## Planning Note

There are now two valid ways to choose the next migration target:

- optimize for low-risk rollout by starting with the recommended next targets above
- optimize for operational impact by prioritizing the high-use harnesses, even when they sit in `Medium` or `Special-Case`

In practice, the best sequence is usually mixed:

1. complete a few `Easy` migrations to lock down the process
2. move to high-use `Medium` harnesses
3. handle high-use `Special-Case` harnesses once the helper and guide are stable
