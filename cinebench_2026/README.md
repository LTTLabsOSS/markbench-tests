# Cinebench 2026

Runs a single test of Cinebench 2026 and reads the score result from the output.

## Prerequisites

- Python 3.10+
- [Download Cinebench 2026 x86_64](https://mx-app-blob-prod.maxon.net/mx-package-production/website/windows/maxon/cinebench/Cinebench2026_win_x86_64.zip)
- Extract the Cinebench files to `C:\Cinebench2026`. The path to the exe should be `C:\Cinebench2026\Cinebench.exe`
- Run Cinebench once manually to accept the EULA; Close Cinebench once EULA has been accepted.

## Options

- `-t` or `--test`: Specifies the Cinebench test to run. Can be one of three options: `cpu-single-core`, `cpu-multi-core` or `gpu`. Any other value will throw an error.

## Output

report.json
- `test`: The name of the selected test
- `score`: The score as output by Cinebench
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds