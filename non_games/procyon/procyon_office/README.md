# UL Procyon Office Productivity

Runs the UL Procyon Office Productivity benchmark and reads the Performance Score result from the output.

## Prerequisites

- Python 3.10+
- UL Procyon installed in default location and activated with at least the Office Productivity tests
- Office Productivity Benchmark DLC installed
- Office 365 installed and activated

## Output

report.json
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `test`: The name of the selected benchmark
- `test_version`: The version of the benchmark
- `procyon_version`: The version of Procyon used
- `score`: The benchmark score