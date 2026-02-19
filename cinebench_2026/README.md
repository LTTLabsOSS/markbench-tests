# Cinebench 2026

Runs a single test of Cinebench 2026 and reads the score result from the output.

## Prerequisites

- Python 3.10+
- [Download Cinebench 2026 x86_64](https://mx-app-blob-prod.maxon.net/mx-package-production/website/windows/maxon/cinebench/Cinebench2026_win_x86_64.zip)
- Extract the Cinebench files to `C:\Cinebench2026`. The path to the exe should be `C:\Cinebench2026\Cinebench.exe`
- Run Cinebench once manually to accept the EULA; Close Cinebench once EULA has been accepted.

## Options

- `-t` or `--test`: Specifies the Cinebench test to run. Can be one of four options: `cpu-single-thread`, `cpu-single-core`, `cpu-multi-thread` or `gpu`. Any other value will throw an error.
- Test options available in Markbench: `cpu-single-thread` (1 thread), `cpu-single-core` (1 core that supports SMT), `cpu-multi-thread` (all CPU threads), `cpu-1/x-thread` (runs single thread and multi thread tests), `cpu-all` (runs all 3 CPU based tests), `gpu` (runs GPU test), `all` (runs all available Cinebench 2026 tests)

## Output

report.json
- `test`: The name of the selected test
- `score`: The score as output by Cinebench
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds