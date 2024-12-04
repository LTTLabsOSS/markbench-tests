# Changelog

All notable changes to this project will be documented in this file.

Changes are grouped by the date they are merged to the main branch of the repository and are ordered from newest to oldest. Dates use the ISO 8601 extended calendar date format, i.e. YYYY-MM-DD.

## 2024-12-04

- Update some timings in RDR2 harness.

## 2024-12-03

- Update encoding presets.

## 2024-12-02

- Add AMD VCE encoding handbrake presets.

## 2024-11-29

- Fix to Handbrake encoding harness.

## 2024-11-20

- Add Alan Wake 2 test harness.
- Add Tiny Tina's Wonderlands harness back with updates.

## 2024-11-05

- Correct typos in MSI Kombustor and PugetBench harnesses.

## 2024-10-25

- Update test name in y-cruncher harness to not be the tuning used.
- Update PugetBench harness to use the latest benchmark version available.
- Fix to Cyberpunk 2077 harness not creating artifact manifest.

## 2024-10-18

- Updated Cyberpunk 2077 harness to take screenshots of settings and results.

## 2024-10-10

- Added a harness for the Black Myth Wukong Benchmark tool

## 2024-10-04

- Implemented the artifact manager to capture screenshots of in game settings and config for atomic heart
- Added steam build ID tracking to atomic heart

## 2024-10-03

- Implemented the artifact manager to capture screenshots of in game settings and results for the following games:
  - Cities Skylines 2
  - Counterstrike 2
  - F1 23
  - Grid Legends
  - Returnal
  - Total War Pharaoh
  - Total War Warhammer 3
- Also implemented steam build ID tracking for the same games

## 2024-09-23

- Add screen splitting to Keras Service.

## 2024-9-20

- Add Grid Legends test harness.
- Add Total War: Pharaoh harness.

## 2024-09-13

- Update godot compile harness with some path fixes.
- Add back Shadow of The Tomb Raider harness that uses Keras.

## 2024-09-06

- Add `artifacts.py` to `harness_utils` for capturing test artifacts.

## 2024-08-30

- Add Stellaris harness based on one_year console command.
- Add City Skylines 2 harness.

## 2024-08-29

- Update blender harness to support different scenes.

## 2024-08-22

- Fixed some bugs with handbrake harness.

## 2024-08-22

- Add godot compile harness.

## 2024-08-16

- Add handbrake test harness.

## 2024-07-29

- Update Y Cruncher test to use version 0.8.5.9543 of Y Cruncher

## 2024-07-08

- Add initial c-ray harness.

## 2024-07-05

- Add initial primesieve harness.

## 2024-06-21

- Update y-cruncher version, and change parameter to 1b from 5b to loosen memory constraints.
- Update y-cruncher to run 5 times and average the score.
- Update 7-Zip to used a locked version, 24.07.
- Update 7-Zip to iterate 3 times each test run.

## 2024-02-20

- Fix type error in DOTA2 `read_config` utility function

## 2024-02-16

- Update DOTA 2 test utils script to check for alternative file path when attempting to read video config file if initial file is not found
- small tweak to mouse input timings in Total War: Warhammer III test script

## 2024-01-04

- Update DOTA 2 test harness to use fallback values and not fail when unable to mark test start or end times

## 2024-01-01

- Update start and end time marking strategies for Atomic Heart test harness
- Update start and end time marking strategies for F1 23 test harness
- Update start and end time marking strategies for TLoU: Part I test harness

## 2023-12-26

- Fix Blender Benchmark harness not running on device type gpu when Intel Arc GPU present.
- Update non-game benchmark reports to fit new schema. This is for downstream reporting compatibility.

## 2023-12-19

- Update menu navigation and start/end time marking for Rocket League harness
- Update Returnal harness to not fail if end time prompt not found
- Update menu navigation and start/end time marking strategies for Cyberpunk 2077 test harness

## 2023-12-13

- Add initial 3DMark harness.

## 2023-12-12

- Update strategies for marking start and end time in Returnal test harness
- Minor changes to logging output in DOTA 2 and Total War: Warhammer III test harnesses
- Update Cinebench test harness to allow for sequential runs of different Cinebench performance tests

## 2023-12-07

- Update DOTA 2 test harness
  - Track configuration file
  - Update script timings
  - Update README and LICENSES
- Update Rocket League test harness
  - Update inputs for main menu navigation
- Update Total War: Warhammer III test harness
  - Update strategies for marking start/end times
- Rename `Included Binaries` section in LICENSES.md to `Required Binaries`

## 2023-12-05

- Update strategies for marking benchmark start and end times in DOTA 2 test harness

## 2023-11-23

<!-- cspell:disable-next-line -->
- Fix issues with links in `CONTRIBUTING.MD` found by @chomes and @OwenHunter

## 2023-11-22

- Remove deprecated test harnesses
  - CS:GO
  - FarCry6
  - Hitman 3
  - Overwatch
  - Shadow of the Tomb Raider
  - Tiny Tina's Wonderland
- Remove unused dependencies

## 2023-11-10

- Deprecate CS:GO test harness.

## 2023-11-06

- Add Cinebench 2024 test harness.
- Remove deprecated Cinebench R23 harness.

## 2023-10-19

- Add Rocket League test harness.
- Add Dota 2 test harness.

## 2023-10-18

- Add Blender barbershop render test harness.

## 2023-10-03

<!-- cspell:disable-next-line -->
- Fix typos found by community members @TheDevMinerTV, @KikisGamingService, @seanmrice, @Intron014, @Jcraft153

## 2023-09-29

- Add readme file to the game settings directory.
- Add logging to `harness_utils.misc.remove_files` when attempting to remove a file that doesn't exist.
- Fix MSI Kombustor harness failing when benchmark option is False

## 2023-09-27

- First