# F1 24 Stress

Runs F1 24 benchmark mode as a fixed-duration stress test. The harness does not
navigate menus.

## Prerequisites

- Python 3.11+
- F1 24 installed through Steam
- `stress/f1_stress/benchmarks/canada_5_loop.xml`
- Hardware settings XML listed in `stress/f1_stress/f1_stress.toml` and present in `stress/f1_stress/hardware_settings`

## Options

- `--hardware-settings` or `--hardware_settings`: hardware settings XML file to copy. Choices and default come from `stress/f1_stress/f1_stress.toml`.
- `--duration-seconds` or `--duration_seconds`: stress duration in seconds. Default `900`.

The hardcoded benchmark XML is copied to the F1 install `benchmark` folder as
`canada_5_loop.xml`.

To add another hardware settings XML, place it in `stress/f1_stress/hardware_settings`
and add its filename to the `hardware_settings` select `values` in
`stress/f1_stress/f1_stress.toml`.

Selected hardware settings file is always copied to
`Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml`,
overwriting the existing file with that destination name.

The harness launches F1 24 with `-benchmark canada_5_loop.xml`.

## Output

`report.json`

- `test`: `F1 24 Stress`
- `stress_duration_seconds`: requested stress duration
- `start_time`: timestamp when launch command was issued, in milliseconds
- `end_time`: timestamp after termination, in milliseconds
- `version`: Steam build id

No XML artifacts are copied into the run output.
