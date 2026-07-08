# FFXIV Dawntrail Benchmark

Navigates menus to the benchmark then runs it.

##Important information:

There are a few things that must be done for this harness to run properly, they are as follows:
- Must exit the settings UI on Graphics Settings 1 tab, by pressing OK (the UI state saves on pressing ok, harness expects it to open on GS1, if you press ok while on another tab the harness will fail.)
- That's it actually

## Prerequisites

- Python 3.10+
- Connection to L:/ drive
- OCR service

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
- `score`: (seconds) Combined load_time (texture loading, indicative of SSD perf.)
- `fps_score`: Actual "Score" for the benchmark, indicative of whole PC performance to varying degrees.
