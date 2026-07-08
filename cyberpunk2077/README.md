# Cyberpunk 2077

Navigates menus to the in-game benchmark then runs it.

## Prerequisites

- Python 3.10+
- Cyberpunk 2077 installed
- OCR service
- [No Intro Videos](https://www.nexusmods.com/cyberpunk2077/mods/533) mod downloaded. Place the mod file `basegame_no_intro_videos.archive` in the test folder.

## Output

report.json
- `resolution`: string representing the resolution the test was run at, formatted as "[width]x[height]", e.x. `1920x1080`
- `start_time`: number representing a timestamp of the test's start time in milliseconds
- `end_time`: number representing a timestamp of the test's end time in milliseconds
