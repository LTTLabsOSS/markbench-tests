# F1 24 Stress

Runs F1 24 benchmark mode as a fixed-duration stress test. The harness does not
navigate menus.

## Prerequisites

- Python 3.10+
- F1 24 installed through Steam
- Benchmark XML at `f1_stress/example_benchmark.xml`
- Hardware settings XML at `f1_stress/config/hardwaresettings/hardware_settings_config.xml`

## Options

- `--duration-seconds` or `--duration_seconds`: stress duration in seconds. Default `900`.

Benchmark XML and hardware settings XML paths are static. The harness copies:

- `f1_stress/config/hardwaresettings/hardware_settings_config.xml` to `Documents\My Games\F1 24\hardwaresettings`.

The harness launches F1 24 with `-benchmark` pointed at the absolute path for
`f1_stress/example_benchmark.xml`.

## Output

`report.json`

- `test`: `F1 24 Stress`
- `stress_duration_seconds`: requested stress duration
- `start_time`: timestamp when launch command was issued, in milliseconds
- `end_time`: timestamp after termination, in milliseconds
- `version`: Steam build id

No XML artifacts are copied into the run output.
