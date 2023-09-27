# Procedure - Returnal Tests

Returnal is installed via Steam, and considered automated for runs via Markbench. Game settings must be changed using the game launcher prior to a scheduled run in Markbench, and the launcher closed prior to setting up Markbench.

In Markbench, select the *Returnal* Test from the list on the left side of the Run Test(s) tab and ensure that the *Run* checkbox beside it is checked. Fill in the settings as follows:

- Project Slug should be the same as the Project Slug you are generating data for
- Test Parameter should be the same as the Test Parameter you are selecting to run, e.g. 'Games-1080', 'Games-1440', 'Games-2160' etc
- Scheduler Delay should be set to *30*
- Recording Delay &amp; Recording Timeout should be set to 0
- Repeat should be set to a minimum of *3* for a default run, unless changes are otherwise require

## 1920x1080

### Games-1080

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *1920 x 1080*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ocaH6h3gAp0u9MAb-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ocaH6h3gAp0u9MAb-1080-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/nj1qeCCY4dO9uT6R-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/nj1qeCCY4dO9uT6R-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/6rhmIWYNd2NWbtDt-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/6rhmIWYNd2NWbtDt-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/iJLNnUOtxcDnAHPE-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/iJLNnUOtxcDnAHPE-rast-3.png)

### Games-1080-DLSS3

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *1920 x 1080*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 1080 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/zJCEPJDuqbheylQX-video-settings-1080-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/zJCEPJDuqbheylQX-video-settings-1080-dlss3.png)

[![graphics settings 1 1080 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/eVEglfSd803z3Gil-graphics-settings-1-1080-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/eVEglfSd803z3Gil-graphics-settings-1-1080-dlss3.png)![graphics settings 2 1080 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/0x0SrfsFMG6h9lHw-graphics-settings-2-1080-dlss3.png)

[![graphics settings 3 1080 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/bwxkqYxHI7Cd093D-graphics-settings-3-1080-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/bwxkqYxHI7Cd093D-graphics-settings-3-1080-dlss3.png)

![graphics settings 4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/Lsh28cgioUFAizuK-graphics-settings-4.png)

### Games-1080-DLSS3-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *1920 x 1080*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 1080 dlss3RT.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/k08uu23Xx7dCCzVf-video-settings-1080-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/k08uu23Xx7dCCzVf-video-settings-1080-dlss3rt.png)

### [![graphics settings 1 1080 dlss3RT.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/KOP0lqzWfLonC99P-graphics-settings-1-1080-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/KOP0lqzWfLonC99P-graphics-settings-1-1080-dlss3rt.png)

[![graphics settings 2 1080 dlss3RT.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/PTKOVHFzMecRn6Md-graphics-settings-2-1080-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/PTKOVHFzMecRn6Md-graphics-settings-2-1080-dlss3rt.png)

[![graphics settings 3 1080 dlss3RT.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/r4LkqD780O2q8GjJ-graphics-settings-3-1080-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/r4LkqD780O2q8GjJ-graphics-settings-3-1080-dlss3rt.png)

[![graphics settings 4 1080 dlss3RT.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/Mhy8cvugZBXhNHGk-graphics-settings-4-1080-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/Mhy8cvugZBXhNHGk-graphics-settings-4-1080-dlss3rt.png)

### Games-1080-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *1920 x 1080*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 1080rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/oFzhSMuOz7TGmJcs-video-settings-1080rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/oFzhSMuOz7TGmJcs-video-settings-1080rt.png)

[![graphics settings 1 1080rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/xER7z8iwKjpaGACD-graphics-settings-1-1080rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/xER7z8iwKjpaGACD-graphics-settings-1-1080rt.png)

[![graphics settings 2 1080rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/edWz0BmCuoPHmL7A-graphics-settings-2-1080rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/edWz0BmCuoPHmL7A-graphics-settings-2-1080rt.png)

[![graphics settings 3 1080rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/JEAVTstpQjse8ZA1-graphics-settings-3-1080rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/JEAVTstpQjse8ZA1-graphics-settings-3-1080rt.png)

[![graphics settings 4 1080rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/jy6Xv50GQIBTFCCg-graphics-settings-4-1080rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/jy6Xv50GQIBTFCCg-graphics-settings-4-1080rt.png)

## 2560x1440

### Games-1440

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *2560 x 1440*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/Qwfn2OjGk1FLDNGR-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/Qwfn2OjGk1FLDNGR-1440-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/4VVIlsi3axJt6YXP-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/4VVIlsi3axJt6YXP-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/FiuFOQKjD1iUIdrh-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/FiuFOQKjD1iUIdrh-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/Qox39XnapkSWZ5BF-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/Qox39XnapkSWZ5BF-rast-3.png)

### Games-1440-DLSS3

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *2560 x 1440*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/bdxifo3xM9iD9wYt-video-settings-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/bdxifo3xM9iD9wYt-video-settings-dlss3.png)

[![graphics settings 1 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/TGv9SmkLLdedQiQT-graphics-settings-1-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/TGv9SmkLLdedQiQT-graphics-settings-1-dlss3.png)

[![graphics settings 2 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/Gs7sK65vi13Iu6kg-graphics-settings-2-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/Gs7sK65vi13Iu6kg-graphics-settings-2-dlss3.png)

[![graphics settings 3 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/OewBUE0x5uW39EeL-graphics-settings-3-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/OewBUE0x5uW39EeL-graphics-settings-3-dlss3.png)

[![graphics settings 4 dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/5D3ofcIMaTGlOYlr-graphics-settings-4-dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/5D3ofcIMaTGlOYlr-graphics-settings-4-dlss3.png)

### Games-1440-DLSS3-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *2560 x 1440*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/yECXQp3iqlsfga97-video-settings-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/yECXQp3iqlsfga97-video-settings-dlss3rt.png)

[![graphics settings 1 dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/mihD2tU4BtbmJbjb-graphics-settings-1-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/mihD2tU4BtbmJbjb-graphics-settings-1-dlss3rt.png)

[![graphics settings 2 dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/zc3lOHpsagwF2REu-graphics-settings-2-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/zc3lOHpsagwF2REu-graphics-settings-2-dlss3rt.png)

[![graphics settings 3 dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/JSL8Pkr7oYkCFHGf-graphics-settings-3-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/JSL8Pkr7oYkCFHGf-graphics-settings-3-dlss3rt.png)

[![graphics settings 4 dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/JbreTU0XoHiLGIuA-graphics-settings-4-dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/JbreTU0XoHiLGIuA-graphics-settings-4-dlss3rt.png)

### Games-1440-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *2560 x 1440*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 1440rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/QccBg6BJVpmzllbq-video-settings-1440rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/QccBg6BJVpmzllbq-video-settings-1440rt.png)

[![graphics settings 1 1440rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/HjmFV4ZP3AteGGNM-graphics-settings-1-1440rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/HjmFV4ZP3AteGGNM-graphics-settings-1-1440rt.png)

[![graphics settings 2 1440rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/X02kVFwd68MrFjDy-graphics-settings-2-1440rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/X02kVFwd68MrFjDy-graphics-settings-2-1440rt.png)

[![graphics settings 3 1440rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/S6YeFoiA681FYDK8-graphics-settings-3-1440rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/S6YeFoiA681FYDK8-graphics-settings-3-1440rt.png)

[![graphics settings 4 1440rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/R3LSNxrkgL4oSqQi-graphics-settings-4-1440rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/R3LSNxrkgL4oSqQi-graphics-settings-4-1440rt.png)

## 3840x2160

### Games-2160

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *3840 x 2160*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/JxY3HpLzWUw2uTvL-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/JxY3HpLzWUw2uTvL-2160-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/I7rGiCQ0ixIYwJCn-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/I7rGiCQ0ixIYwJCn-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/6bOn6Ou3duc0I0ID-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/6bOn6Ou3duc0I0ID-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/scaled-1680-/QoTaJmiduvvT2jEZ-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-04/QoTaJmiduvvT2jEZ-rast-3.png)

### Games-2160-DLSS3

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *3840 x 2160*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Lighting, Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *off*
- Ensure Screen-Space Reflections are set to *on*
- Ensure Ray-Traced Reflections are set to *off*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 2160dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/qXQc4Y1S6LpRtHU1-video-settings-2160dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/qXQc4Y1S6LpRtHU1-video-settings-2160dlss3.png)

[![graphics settings 1 2160dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/n6g3Ab3t6HJCgOdM-graphics-settings-1-2160dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/n6g3Ab3t6HJCgOdM-graphics-settings-1-2160dlss3.png)

[![graphics settings 2 2160dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/Wg2ojkCcgGhLyWwB-graphics-settings-2-2160dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/Wg2ojkCcgGhLyWwB-graphics-settings-2-2160dlss3.png)

[![graphics settings 3 2160dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/QkuL07nU9kkL11iC-graphics-settings-3-2160dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/QkuL07nU9kkL11iC-graphics-settings-3-2160dlss3.png)

[![graphics settings 4 2160dlss3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/QGCiCZr7p30Vtss1-graphics-settings-4-2160dlss3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/QGCiCZr7p30Vtss1-graphics-settings-4-2160dlss3.png)

### Games-2160-DLSS3-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *3840 x 2160*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations is set to *DLSS*
- Ensure DLSS SR is set to *quality*
- Ensure DLSS Frame Gen is set to on
- Ensure DLSS Sharpness is set to *50%*
- Ensure Nvidia Reflex is set to *on*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 2160dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/qOwhyUHg9xCXAUEJ-video-settings-2160dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/qOwhyUHg9xCXAUEJ-video-settings-2160dlss3rt.png)

[![graphics settings 1 2160dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/2IYteN9NI5dXiYQz-graphics-settings-1-2160dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/2IYteN9NI5dXiYQz-graphics-settings-1-2160dlss3rt.png)

[![graphics settings 2 2160dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/2nTsCtPOau4WxsT2-graphics-settings-2-2160dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/2nTsCtPOau4WxsT2-graphics-settings-2-2160dlss3rt.png)

[![graphics settings 3 2160dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/X2n0uektskACSd8M-graphics-settings-3-2160dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/X2n0uektskACSd8M-graphics-settings-3-2160dlss3rt.png)

[![graphics settings 4 2160dlss3rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/VQZc54xagIe2GZlP-graphics-settings-4-2160dlss3rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/VQZc54xagIe2GZlP-graphics-settings-4-2160dlss3rt.png)

### Games-2160-Rt

Once the game loads, hit Escape. Navigate to Settings.

#### Video &gt; Display

- Set Display Mode to *Fullscreen*
- Set Screen Resolution to *3840 x 2160*

Click alt then space to set the resolution

#### Graphics

- Set Graphics Preset to *Epic*
    - This should ensure that Environment, and Post Processing settings are set correctly, but you should verify them for every run.
- Ensure VSync is set to *Off*
- Ensure Max Frames per Second is set to *Infinite FPS*
- Ensure Screen Optimizations are set to *off*
- Ensure Ray-Traced Shadows are set to *Epic*
- Ensure Screen-Space Reflections are set to on
- Ensure Ray-Traced Reflections are set to *Epic*

Click *escape*, then scroll to suspend/quit, press *space*, then hold *space* to "suspend" the run, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![video settings 2160rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/SvpLpVSoVDOVj2i5-video-settings-2160rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/SvpLpVSoVDOVj2i5-video-settings-2160rt.png)

[![graphics settings 1  2160rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/99RZSrDN7FxAP5UW-graphics-settings-1-2160rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/99RZSrDN7FxAP5UW-graphics-settings-1-2160rt.png)

[![graphics settings 2 2160rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/XuycvRAxaHf8VKNe-graphics-settings-2-2160rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/XuycvRAxaHf8VKNe-graphics-settings-2-2160rt.png)

[![graphics settings 3 2160rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/LHiXtPNjgQnGRIlx-graphics-settings-3-2160rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/LHiXtPNjgQnGRIlx-graphics-settings-3-2160rt.png)

[![graphics settings 4 2160rt.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/19xqIDwuGK5q76LM-graphics-settings-4-2160rt.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/19xqIDwuGK5q76LM-graphics-settings-4-2160rt.png)