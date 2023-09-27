# Procedure - Cyberpunk 2077 Tests

Cyberpunk 2077 is installed via Steam, and considered automated for runs via Markbench. Game settings must be changed using the game launcher prior to a scheduled run in Markbench, and the launcher closed prior to setting up Markbench.

In Markbench, select the *Cyberpunk 2077* Test from the list on the left side of the Run Test(s) tab and ensure that the *Run* checkbox beside it is checked. Fill in the settings as follows:

- Project Slug should be the same as the Project Slug you are generating data for
- Test Parameter should be the same as the Test Parameter you are selecting to run, e.g. 'Games-1080', 'Games-1440', 'Games-2160' etc
- Scheduler Delay should be set to *5*
- Recording Delay &amp; Recording Timeout should be set to 0
- Repeat should be set to a minimum of *3* for a default run, unless changes are otherwise required

## 1920x1080

### Games-1080

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *1920x1080*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it. Click apply.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/xe9QbZJ7VUWtWrWL-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/xe9QbZJ7VUWtWrWL-1080-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rast-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/6tIiUw5i2vLPGS7L-rast-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6tIiUw5i2vLPGS7L-rast-4.png)

### Games-1080-DLSS3

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *1920x1080*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/08gHPJfZQj3FKsLW-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/08gHPJfZQj3FKsLW-1080-1.png)

[![dlss3-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/IRpODCOzjvTeBI4e-dlss3-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/IRpODCOzjvTeBI4e-dlss3-1.png)

[![dlss3-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/KHbOvf0BT9mZBe6S-dlss3-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/KHbOvf0BT9mZBe6S-dlss3-2.png)

[![dlss3-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/YLf6797w4J8pwx3M-dlss3-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/YLf6797w4J8pwx3M-dlss3-3.png)

### Games-1080-DLSS3-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *1920x1080*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/lCmjj1l0pL8Q6WnL-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/lCmjj1l0pL8Q6WnL-1080-1.png)

[![dlss3_rt-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)

[![dlss3_rt-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)

[![dlss3_rt-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/scRFXgXGDUKpKWTk-dlss3-rt-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scRFXgXGDUKpKWTk-dlss3-rt-3.png)

[![dlss3_rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/djsOSkNEAG8g97iZ-dlss3-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/djsOSkNEAG8g97iZ-dlss3-rt-4.png)

### Games-1080-FSR

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *1920x1080*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its right arrow until *Quality* is shown. Locate the AMD FSR 2.1 Image Sharpening setting, click its right arrow until *0.50* is shown, then click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZV9Okn4fcccFziY5-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZV9Okn4fcccFziY5-1080-1.png)

[![fsr-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/trAk1yyTBrqrRq2K-fsr-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/trAk1yyTBrqrRq2K-fsr-1.png)

[![fsr-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/wtOZe4LnaGbHF3NV-fsr-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/wtOZe4LnaGbHF3NV-fsr-2.png)

[![fsr-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/JnmNpMp4QlFrYenC-fsr-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/JnmNpMp4QlFrYenC-fsr-3.png)

### Games-1080-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *1920x1080*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1080-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/xe9QbZJ7VUWtWrWL-1080-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/xe9QbZJ7VUWtWrWL-1080-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/yDiMcwxFlcvIwgrU-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/yDiMcwxFlcvIwgrU-rt-4.png)

[![rt-5.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/qqKIrJH53fYFQWsj-rt-5.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/qqKIrJH53fYFQWsj-rt-5.png)

## 2560x1440

### Games-1440

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *2560x1440*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/3gkwsWeIo9GkSxVo-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/3gkwsWeIo9GkSxVo-1440-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rast-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/6tIiUw5i2vLPGS7L-rast-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6tIiUw5i2vLPGS7L-rast-4.png)

### Games-1440-DLSS3

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *2560x1440*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/cKw7cd5OA5IoSWbf-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/cKw7cd5OA5IoSWbf-1440-1.png)

[![dlss3-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/IRpODCOzjvTeBI4e-dlss3-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/IRpODCOzjvTeBI4e-dlss3-1.png)

[![dlss3-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/KHbOvf0BT9mZBe6S-dlss3-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/KHbOvf0BT9mZBe6S-dlss3-2.png)

[![dlss3-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/YLf6797w4J8pwx3M-dlss3-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/YLf6797w4J8pwx3M-dlss3-3.png)

### Games-1440-DLSS3-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *2560x1440*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/y3N6ufcijRbJn3YJ-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/y3N6ufcijRbJn3YJ-1440-1.png)

[![dlss3_rt-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)

[![dlss3_rt-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)

[![dlss3_rt-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/scRFXgXGDUKpKWTk-dlss3-rt-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scRFXgXGDUKpKWTk-dlss3-rt-3.png)

[![dlss3_rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/djsOSkNEAG8g97iZ-dlss3-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/djsOSkNEAG8g97iZ-dlss3-rt-4.png)

### Games-1440-FSR

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *2560x1440*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its right arrow until *Quality* is shown. Locate the AMD FSR 2.1 Image Sharpening setting, click its right arrow until *0.50* is shown, then click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/gepBRIDOdD5tlWEH-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/gepBRIDOdD5tlWEH-1440-1.png)

[![fsr-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/trAk1yyTBrqrRq2K-fsr-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/trAk1yyTBrqrRq2K-fsr-1.png)

[![fsr-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/wtOZe4LnaGbHF3NV-fsr-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/wtOZe4LnaGbHF3NV-fsr-2.png)

[![fsr-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/JnmNpMp4QlFrYenC-fsr-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/JnmNpMp4QlFrYenC-fsr-3.png)

### Games-1440-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *2560x1440*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![1440-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/MXPecQWl33T3XIaG-1440-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/MXPecQWl33T3XIaG-1440-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/yDiMcwxFlcvIwgrU-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/yDiMcwxFlcvIwgrU-rt-4.png)

[![rt-5.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/qqKIrJH53fYFQWsj-rt-5.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/qqKIrJH53fYFQWsj-rt-5.png)

## 3840x2160

### Games-2160

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *3840x2160*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/UeGVAyy6yh7qQKw4-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/UeGVAyy6yh7qQKw4-2160-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rast-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/6tIiUw5i2vLPGS7L-rast-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6tIiUw5i2vLPGS7L-rast-4.png)

### Games-2160-DLSS3

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *3840x2160*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/b3diyCpg003zWD5O-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/b3diyCpg003zWD5O-2160-1.png)

[![dlss3-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/IRpODCOzjvTeBI4e-dlss3-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/IRpODCOzjvTeBI4e-dlss3-1.png)

[![dlss3-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/KHbOvf0BT9mZBe6S-dlss3-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/KHbOvf0BT9mZBe6S-dlss3-2.png)

[![dlss3-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/YLf6797w4J8pwx3M-dlss3-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/YLf6797w4J8pwx3M-dlss3-3.png)

### Games-2160-DLSS3-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *3840x2160*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Next, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

Finally, locate the DLSS Frame Generation setting. Toggle it to *On*, then click Apply at the bottom of the screen. Locate the DLSS Super Resolution setting, and click its right arrow until *Quality* is shown. Ensure that DLSS Sharpness is set to *0.50*, and click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/oB63TM8bpm8GCvsU-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/oB63TM8bpm8GCvsU-2160-1.png)

[![dlss3_rt-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/x1d0t5FdBGGbCgQc-dlss3-rt-1.png)

[![dlss3_rt-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/0lVfz5Z9xuzeKjM8-dlss3-rt-2.png)

[![dlss3_rt-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/scRFXgXGDUKpKWTk-dlss3-rt-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scRFXgXGDUKpKWTk-dlss3-rt-3.png)

[![dlss3_rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/djsOSkNEAG8g97iZ-dlss3-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/djsOSkNEAG8g97iZ-dlss3-rt-4.png)

### Games-2160-FSR

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *3840x2160*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its right arrow until *Quality* is shown. Locate the AMD FSR 2.1 Image Sharpening setting, click its right arrow until *0.50* is shown, then click Apply at the bottom of the screen.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *Off*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/AeyocwOvAHRpDANr-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/AeyocwOvAHRpDANr-2160-1.png)

[![fsr-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/trAk1yyTBrqrRq2K-fsr-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/trAk1yyTBrqrRq2K-fsr-1.png)

[![fsr-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/wtOZe4LnaGbHF3NV-fsr-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/wtOZe4LnaGbHF3NV-fsr-2.png)

[![fsr-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/JnmNpMp4QlFrYenC-fsr-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/JnmNpMp4QlFrYenC-fsr-3.png)

### Games-2160-Rt

In-game, navigate to Settings.

#### Video

- Ensure VSync is set to *Off*
- Ensure Maximum FPS is set to *Off*
- Ensure Windowed Mode is set to *Fullscreen*
- Set Resolution to *3840x2160*

#### Graphics

Locate the Quick Preset setting at the top of the page. Click its right arrow selector until *Ray Tracing: Ultra* is shown.

- Ensure Texture Quality is set to *High*

Under Resolution Scaling, locate the AMD FSR 2.1 Image Sharpening setting. Click its right arrow twice, until a setting other than 0 is shown, then click Apply at the bottom of the screen. Locate the AMD FSR 2.1 Image Sharpening setting again, and click its left arrow until 0 is shown, then click Apply at the bottom of the screen.

Under Resolution Scaling, locate the AMD FidelityFX Super Resolution 2.1 setting. Click its left arrow until *Off* is shown. This will also <span style="text-decoration: underline;">**hide**</span> (but not disable) the Image Sharpening setting below it.

- Ensure Screen Space Reflections Quality is set to *Ultra*
- Ensure Ray Tracing is set to *On*
- Ensure Ray Tracing Reflections is set to *On*
- Ensure Ray-Traced Sun Shadows is set to *On*
- Ensure Ray-Traced Local Shadows is set to *On*
- Ensure Ray-Traced Lighting is set to *Ultra*

Once settings are adjusted correctly, exit the game properly using the menu navigation. Do not exit the game using Alt + F4 or End Task from Task Manager. Run tests via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

[![2160-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/sux4Nd8MNE3XCFxF-2160-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/sux4Nd8MNE3XCFxF-2160-1.png)

[![rast-1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/ZGcbqTeyMO4jnePX-rast-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/ZGcbqTeyMO4jnePX-rast-1.png)

[![rast-2.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/bIQ3TrPmflZhuM4P-rast-2.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/bIQ3TrPmflZhuM4P-rast-2.png)

[![rast-3.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/RJjcAYJcvygNXJfo-rast-3.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/RJjcAYJcvygNXJfo-rast-3.png)

[![rt-4.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/yDiMcwxFlcvIwgrU-rt-4.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/yDiMcwxFlcvIwgrU-rt-4.png)

[![rt-5.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/scaled-1680-/qqKIrJH53fYFQWsj-rt-5.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/qqKIrJH53fYFQWsj-rt-5.png)