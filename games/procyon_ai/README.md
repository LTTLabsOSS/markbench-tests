# UL Procyon AI Computer Vision

Runs the UL Procyon AI Computer Vision benchmark using a specified engine and reads the Performance Score result from the output.

## Prerequisites

- Python 3.10+
- UL Procyon installed in default location and activated with at least the AI tests
- AI Computer Vision Benchmark DLC installed

## Options

- `--engine` Specifies the hardware to benchmark.

## Output

report.json
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `test`: The name of the selected benchmark
- `test_version`: The version of the benchmark
- `device_name`: The name of the device tested
- `procyon_version`: The version of Procyon used
- `score`: The text generation scores