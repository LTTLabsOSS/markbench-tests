# PCMark 10 Storage

Runs the PCMark 10 Storage benchmark (specifying either quick or full test) and reads the Score result from the output.

## Prerequisites

- Python 3.10+
- PCMark 10 with the Storage benchmark installed
- At least 80GB (Full) or 10GB (Quick) free space on the drive to test

## Options

- `--drive_letter` : Allows you to specify a drive letter (default is C)
- `--test` : Specifies which test to run [full,quick] 
- `--drive_prepare` : Allows a user to target a specific drive filled % size [no,25,50,75,90]

## Output

report.json
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `test`: The name of the selected benchmark
- `test_version`: The version of the benchmark
- `pcmark10_version`: The version of PCMark10 used
- `test_parameter`: Which test was ran
- `score`: The storage test score
