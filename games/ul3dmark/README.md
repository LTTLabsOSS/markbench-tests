# 3DMark

Runs one of the 3DMark benchmark scenes and reads the Performance Graphics Score result from the output.

## Prerequisites

- Python 3.10+
- 3DMark Professional Edition installed in default location and activated.
- Desired benchmarks are downloaded,.

## Options

- `--benchmark` Specifies the benchmark to run.

## Output

report.json
- `test`: The name of the selected benchmark
- `score`: 3DMark gpu score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds