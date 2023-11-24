# Procedure - DOTA 2 Tests

DOTA 2 is installed via Steam, and considered automated for runs via Markbench. Game settings must be changed in-game prior to a scheduled run in Markbench, and the game exited prior to setting up Markbench.

In Markbench, select the *DOTA2 test from the list on the left side of the Run Test(s) tab and ensure that the *Run* checkbox beside it is checked. Fill in the settings as follows:

- Project Slug should be the same as the Project Slug you are generating data for
- Test Parameter should be the same as the Test Parameter you are selecting to run, e.g. 'Games-1080', 'Games-1440', 'Games-2160' etc
- Scheduler Delay should be set to *5*
- Recording Delay &amp; Recording Timeout should be set to 0
- Repeat should be set to a minimum of *3* for a default run, unless changes are otherwise required

<p class="callout warning">Do not exit the game after setting display and graphics settings using Alt + F4 or End Process from Task Manager</p>

## 1920x1080

### Games-1080

In-game, navigate to Settings (the cog in the upper left). Then select the Video tab.

#### Video

- Select Use advanced settings
- Ensure the aspect ratio is correct for the resolution or else it won't display it in the list
- Set Resolution to *1920 x 1080 (with the highest Hz option available)*
- Set Display Mode to *Exclusive Fullscreen*
- Ensure Rendering API is set to Direct3D 11
- Ensure if running an Nvidia graphics card that Nvidia Reflex is disabled
- With Use basic settings selected, drag the slider all the way to the Best Looking option

Apply changes, then to exit click the cog wheel again and click the red icon in the upper right to exit to the desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![dota 2 1080.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/scaled-1680-/GxNMkdbBDSY2Aylb-dota-2-1080.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/GxNMkdbBDSY2Aylb-dota-2-1080.png)

## 2560x1440

### Games-1440

In-game, navigate to Settings (the cog in the upper left). Then select the Video tab.

#### Video

- Select Use advanced settings
- Ensure the aspect ratio is correct for the resolution or else it won't display it in the list
- Set Resolution to *2560 x 1440 (with the highest Hz option available)*
- Set Display Mode to *Exclusive Fullscreen*
- Ensure Rendering API is set to Direct3D 11
- Ensure if running an Nvidia graphics card that Nvidia Reflex is disabled
- With Use basic settings selected, drag the slider all the way to the Best Looking option

Apply changes, then to exit click the cog wheel again and click the red icon in the upper right to exit to the desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![dota 2 1440.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/scaled-1680-/kPUKaNl8C3yiMY7e-dota-2-1440.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/kPUKaNl8C3yiMY7e-dota-2-1440.png)

## 3840x2160

### Games-2160

In-game, navigate to Settings (the cog in the upper left). Then select the Video tab.

#### Video

- Select Use advanced settings
- Ensure the aspect ratio is correct for the resolution or else it won't display it in the list
- Set Resolution to *3840 x 2160 (with the highest Hz option available)*
- Set Display Mode to *Exclusive Fullscreen*
- Ensure Rendering API is set to Direct3D 11
- Ensure if running an Nvidia graphics card that Nvidia Reflex is disabled
- With Use basic settings selected, drag the slider all the way to the Best Looking option

Apply changes, then to exit click the cog wheel again and click the red icon in the upper right to exit to the desktop. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![dota 2 2160.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/scaled-1680-/Pu4bGAmWwZUI6o0Y-dota-2-2160.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-08/Pu4bGAmWwZUI6o0Y-dota-2-2160.png)