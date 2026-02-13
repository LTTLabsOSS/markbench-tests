# 7-Zip Compression and Decompression Test

A benchmark which uses the built in benchmark utility of 7-Zip. It uses dummy data and then LZMA to compress/decompress it.

## Prerequisites

- Python 3.10+

## Output

report.json
- `score`: the compression and decompression score from the test each in KiB/s
- `version`: version of 7-Zip used.