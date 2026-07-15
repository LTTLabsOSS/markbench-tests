# GravityMark

Runs GravityMark in benchmark mode using the selected graphics API. Stores the results image file.

## Prerequisites

- Python 3.10+
- GravityMark installed in default location. [Download GravityMark](https://gravitymark.tellusim.com/)

## Options

- `-a` or `--api`: Specifies which graphics API to run for GravityMark to use for the benchmark.

Note that while GravityMark supports OpenGLES and Metal, they are not available on Windows and as such, this test script does not provide the option to use them.

## Output

report.json
- `api`: The graphics API used for the test