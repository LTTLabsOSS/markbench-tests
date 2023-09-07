# FurMark Test Harness

## Prerequisites

- Python 3.10+
- MSI Kombuster installed in default path.

This harness expects that MSI Kombuster has been installed on the system using installer defaults.
> Note: Hopefully it will install itself in the future if not present.

## Setup

  1. Follow the setup instructions for the framework. If you have done so, all required python dependencies *should* be installed.
  2. Install MSI Kombuster from `\\10.20.0.27\Users\Linus\Team_Documents\Nikolas\Benchmark_Dependencies\MSI_Kombustor4_Setup_v4.1.16.0_x64.exe`
      1. Follow the installer's defaults.

## Configuration

Below is an example use of this harness as a test in a benchmark configuration.

```yaml
...
...
tests:
  - name: msikombuster
    executable: "msikombuster.py"
    process_name: "MSI-Kombuster-x64.exe"
    asset_paths:
      - 'harness/msikombuster/run'
```

__name__ : _(required)_ name of the test. This much match the name of a directory in the harness folder so the framework
can find the executable and any supplementary files.

__executable__ : _(required)_ the entry point to the test harness. In this case a python script.

__process_name__ : _(required)_ The process name that should be the target for FPS recording (ex: PresentMon).

__asset_paths__: _(optional)_ list of files to aggregate copies of after a successful test run. If a directory path is
given, the contents are copied.


