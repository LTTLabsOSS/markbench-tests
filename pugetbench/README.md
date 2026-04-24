# PugetBench for Creators

This is a test harness to run the test suite [PugetBench for Creators](https://www.pugetsystems.com/pugetbench/creators/) which contains tests for Adobe Photoshop, Adobe Premiere Pro, Adobe After Effects, Adobe Lightroom, and Davinci Resolve Studio. The benchmark it runs is the Standard set.

## Prerequisites

- Python 3.10+
- PugetBench for Creators installed and activated for CLI features.
- Adobe Creative Cloud installed with the appropriate Adobe software
- Davinci Resolve Studio

## Options
- `app_version` : Allows you to specify an app version if multiple versions installed on the system (blank will autodiscover)
- `--app` : Specifies which test to run [premierepro,photoshop,aftereffects,lightroom,resolve]
- `benchmark_version` : Allows you to specify the benchmark version you wish to run (blank will default to latest and prioritize betas)

## Output

report.json
- `test`: The application that was tested.
- `score`: The score extracted from PugetBench.