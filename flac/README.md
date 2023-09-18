# FLAC Audio Encode

Test which encodes Nine in Nails - The Slip in WAV form to [FLAC](https://xiph.org/flac/)

> [FLAC](https://xiph.org/flac/) stands for Free Lossless Audio Codec, an audio format similar to MP3, but lossless, meaning that audio is compressed in FLAC without any loss in quality.

This test tracks how long it takes to encode the song 30 times and the duration is recorded as the score in seconds.

## Prerequisites

- Python 3.10+

## Output

report.json
- `score`: the compression and decompression score from the test each in KiB/s
- `version`: version of FLAC used