# Blender Benchmark

A wrapper for the CLI version of [Blender Benchmark](https://opendata.blender.org/).

## Prerequisites

- Python 3.10+

## Options

- `--scene`: one of four options [all, monster, classroom, junkshop]
- `--device`: cpu or gpu
- `--version`: blender version, examples: "3.6.0", "3.5.0"

## Output

report.json - an array of json objects, each being a report per scene benchmarked.