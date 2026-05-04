# F1 24 Stress

Runs F1 24 benchmark mode as a fixed-duration stress test. The harness does not
navigate menus.

## Prerequisites

- Python 3.11+
- F1 24 installed through Steam
- Benchmark XML listed in `f1_stress.toml` and present in the harness folder
- Hardware settings XML at `f1_stress/config/hardwaresettings/hardware_settings_config.xml`

## Options

- `--benchmark`: benchmark XML file to run. Choices and default come from `f1_stress.toml`.
- `--duration-seconds` or `--duration_seconds`: stress duration in seconds. Default `900`.

To add another benchmark XML, place it in `f1_stress` and add its filename to the
`benchmark` select `values` in `f1_stress.toml`.

Hardware settings path is static. The harness copies:

- `f1_stress/config/hardwaresettings/hardware_settings_config.xml` to `Documents\My Games\F1 24\hardwaresettings`.

The harness launches F1 24 with `-benchmark` pointed at the selected XML's
absolute path.

## Output

`report.json`

- `test`: `F1 24 Stress`
- `stress_duration_seconds`: requested stress duration
- `start_time`: timestamp when launch command was issued, in milliseconds
- `end_time`: timestamp after termination, in milliseconds
- `version`: Steam build id

No XML artifacts are copied into the run output.
