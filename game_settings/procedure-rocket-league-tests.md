# Procedure - Rocket League Tests

Rocket League is installed via the Epic Games Launcher, and considered automated for runs via Markbench. Game settings must be changed in-game prior to a scheduled run in Markbench, and the game exited prior to setting up Markbench. On first load the game will play the tutorial, you do not need to do any inputs till after the 2 minutes of in-game gameplay has finished to exit to the main menu.

In Markbench, select the *Rocket League* test from the list on the left side of the Run Test(s) tab and ensure that the *Run* checkbox beside it is checked. Fill in the settings as follows:

- Project Slug should be the same as the Project Slug you are generating data for
- Test Parameter should be the same as the Test Parameter you are selecting to run, e.g. 'Games-1080', 'Games-1440', 'Games-2160' etc
- Scheduler Delay should be set to *5*
- Recording Delay &amp; Recording Timeout should be set to 0
- Repeat should be set to a minimum of *3* for a default run, unless changes are otherwise required

<p class="callout warning">Do not exit the game after setting display and graphics settings using Alt + F4 or End Process from Task Manager</p>

## 1920x1080

### Games-1080

In the main menu, navigate to Settings. Then go to the Video tab.

#### Video

- Set Resolution to *1920 x 1080*
- Set Display Mode to *Fullscreen*
- Set Anti-Aliasing to Off
- Ensure Render Quality is set to High Quality
- Ensure Render Detail is set to High Quality
- Set Frames Per Second to Uncapped

***Note*** If you're unable to select the correct resolution (as sometimes Rocket League incorrectly detects the right resolutions for your display) you will need to remove the TASystemSettings.ini located in Documents/My Games/Rocket League/TAGame/Config and relaunch the game to get correct video settings detected.

Apply changes, then to exit click Back and click Quit to Desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![RocketLeague-1080.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/scaled-1680-/3OEZQaF10DYSKpxE-rocketleague-1080.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/3OEZQaF10DYSKpxE-rocketleague-1080.png)

## 2560x1440

### Games-1440

In the main menu, navigate to Settings. Then go to the Video tab.

#### Video

- Set Resolution to *2560 x 1440*
- Set Display Mode to *Fullscreen*
- Set Anti-Aliasing to Off
- Ensure Render Quality is set to High Quality
- Ensure Render Detail is set to High Quality
- Set Frames Per Second to Uncapped

***Note*** If you're unable to select the correct resolution (as sometimes Rocket League incorrectly detects the right resolutions for your display) you will need to remove the TASystemSettings.ini located in Documents/My Games/Rocket League/TAGame/Config and relaunch the game to get correct video settings detected.

Apply changes, then to exit click Back and click Quit to Desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![RocketLeague-1440.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/scaled-1680-/a9x1f2mSdnYKK0Ld-rocketleague-1440.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/a9x1f2mSdnYKK0Ld-rocketleague-1440.png)

## 3840x2160

### Games-2160

In the main menu, navigate to Settings. Then go to the Video tab.

#### Video

- Set Resolution to *3840 x 2160*
- Set Display Mode to *Fullscreen*
- Set Anti-Aliasing to Off
- Ensure Render Quality is set to High Quality
- Ensure Render Detail is set to High Quality
- Set Frames Per Second to Uncapped

***Note*** If you're unable to select the correct resolution (as sometimes Rocket League incorrectly detects the right resolutions for your display) you will need to remove the TASystemSettings.ini located in Documents/My Games/Rocket League/TAGame/Config and relaunch the game to get correct video settings detected.

Apply changes, then to exit click Back and click Quit to Desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![RocketLeague-2160.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/scaled-1680-/COlZ5bMKtGzyK5f4-rocketleague-2160.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-11/COlZ5bMKtGzyK5f4-rocketleague-2160.png)