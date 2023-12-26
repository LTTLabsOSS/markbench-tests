# Changelog

All notable changes to this project will be documented in this file.

Changes are grouped by the date they are merged to the main branch of the repository and are ordered from newest to oldest. Dates use the ISO 8601 extended calendar date format, i.e. YYYY-MM-DD.

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