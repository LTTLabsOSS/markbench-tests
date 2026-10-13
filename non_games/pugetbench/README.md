# PugetBench for Creators

This is a test harness to run the test suite [PugetBench for Creators](https://www.pugetsystems.com/pugetbench/creators/) which contains tests for Adobe Photoshop, Adobe Premiere Pro, Adobe After Effects, Adobe Lightroom, Davinci Resolve Studio, and Unreal Engine. You can select either the Standard or Extended run preset.

## Prerequisites

- Python 3.10+
- PugetBench for Creators installed and activated for CLI features.
- Adobe Creative Cloud installed with the appropriate Adobe software
- Davinci Resolve Studio
- Unreal Engine 5.8 or newer

## Options
- `--app` : Specifies which test to run [premierepro,photoshop,aftereffects,lightroom,resolve,unreal]
- `benchmark_version` : Allows you to specify the benchmark version you wish to run (blank will default to latest and prioritize betas)
- `benchmark_type` : Allows you to specify either standard or extended tests for a given benchmark

## Output

report.json
- `test`: The application used for testing.
- `test_parameter` : The targeted test and preset.
- `app_version` : The version for the targeted test.
- `benchmark_version` : The version of the benchmark used.
- `pugetbench_version` : The version of PugetBench used.
- `score`: The score extracted from PugetBench.