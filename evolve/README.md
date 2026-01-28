
# EVOLVE

Runs the EVOLVE benchmark scene and reads all the produced scores.

## Prerequisites

- Python 3.10+
- EVOLVE Advanced, Professional or Enterprise edition installed in default location.

## Options

- `--renderer` Specifies the type of renderer to run with
- `--type` Specifies the method for hardware-accelerated ray-tracing or general rendering to use
- `--preset` Specifies the graphic preset for the benchmark

## Output

Note: Some scores will be zero, depending on the selected renderer, tracing type and capabilities of the hardware.

report-raytracing-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's GPU Raytracing score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-rasterization-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's GPU Rasterization score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-acceleration-structure-build-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's GPU Acceleration Structure Build score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-workgraph-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's GPU Workgraph score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-compute-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's GPU Compute score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-driver-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's Driver score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds

report-energy-score.json
- `test`: The name of the selected rendering options and score specification
- `score`: EVOLVE's Energy score
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
