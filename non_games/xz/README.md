# XZ single core compression

This test uses a build of [XZ Utils](https://github.com/tukaani-project/xz) to compress a 1080p Tech Quickie video at level 9 compression. It measures the duration in milliseconds the first five cores and then averages it for a total score.

> This is test is not suitable for processors that have less than 6 primary performance cores. Running this test on a processor with less will result in including efficiency/small cores in the result, skewing the scores.

## Prerequisites

- Python 3.10+
- 6+ core system

## Output

report.json
- `score`: the average duration in milliseconds 
- `version`: the version of xz utils