# Godot Compile

Compile test which measures the duration to compile Godot 4.7.2 from source (editor target, `d3d12=no`).

The build uses [llvm-mingw](https://github.com/mstorsjo/llvm-mingw) 20261006 (Clang, LLVM 23.1.3) on both x86_64 and arm64, so both architectures are compiled with the same compiler version. The arm64 build is a native Windows on ARM build.

The Godot and llvm-mingw versions are pinned together. Newer compilers can fail on an older Godot's bundled third-party code (Godot 4.4.1 does not build with LLVM 23), so update both together and test a full build first.

## Prerequisites

- Python 3.10+
- On the network drive (see `godot_compile_utils.py`):
  - `godot-4.7.2-stable.zip`, containing a top-level `godot-4.7.2-stable` folder
  - llvm-mingw `ucrt-x86_64` and `ucrt-aarch64` zips for the pinned release

## Options

- `--architecture`: `x86_64` or `arm64`

## Output

report.json
- `score`: duration of compile in seconds
- `version`: version of Godot compiled
- `architecture`: architecture Godot was compiled for
- `compiler`: version string of the llvm-mingw clang used for the build
