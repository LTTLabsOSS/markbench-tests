# Godot Compile

Compile test which measures the duration to compile Godot from source.

The build uses [llvm-mingw](https://github.com/mstorsjo/llvm-mingw) (Clang) on both x86_64 and arm64, so both architectures are compiled with the same compiler version. The arm64 build is a native Windows on ARM build.

## Prerequisites

- Python 3.10+
- llvm-mingw `ucrt-x86_64` and `ucrt-aarch64` zips on the network drive (see `LLVM_MINGW_RELEASE` in `godot_compile_utils.py`)

## Options

- `--architecture`: `x86_64` or `arm64`

## Output

report.json
- `score`: duration of compile in seconds
- `version`: version of Godot compiled
- `architecture`: architecture Godot was compiled for
- `compiler`: version string of the llvm-mingw clang used for the build
