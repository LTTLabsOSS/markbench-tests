# Procedure - Counter-Strike: Global Offensive Tests

Counter Strike: Global Offensive (CS:GO) is installed via Steam, and considered automated for runs via Markbench. Game settings must be changed using the in game menus prior to a scheduled run in Markbench, and the game closed prior to setting up Markbench.

This test uses the benchmark script from [https://github.com/samisalreadytaken/csgo-benchmark](https://github.com/samisalreadytaken/csgo-benchmark).

Markbench automates installing the benchmark script onto the system. However, if your registry key is invalid for some reason (mostly on older installs of CSGO) you will need to copy the script from the .\\Markbench\[Version\]\\harness\\csgo folder labeled as CSGO to the appropriate base installation location of CSGO which by default is "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive".

In Markbench, select the *Counter Strike: Global Offensive* Test from the list on the left side of the Run Test(s) tab and ensure that the *Run* checkbox beside it is checked. Fill in the settings as follows:

- Project Slug should be the same as the Project Slug you are generating data for
- Test Parameter should be the same as the Test Parameter you are selecting to run, e.g. 'Games-1080', 'Games-1440-DX11', 'Games-2160-Rt' etc
- Scheduler Delay should be set to *30*
- Recording Delay &amp; Recording Timeout should be set to 0
- Repeat should be set to a minimum of *3* for a default run, unless changes are otherwise required

## 1920x1080

### Games-1080

Launch the game and go to the settings menu.

#### Game

- Ensure Enable Developer Console is set to *Yes*

#### Video

- Ensure Resolution is set to *1920x1080*
- Ensure display mode is set to *Fullscreen*
- Ensure Laptop Power Savings is set to *Disabled*
- Ensure Global Shadow Quality is set to *High*
- Ensure Model / Texture Detail is set to *High*
- Ensure Texture Streaming is set to *Disabled*
- Ensure Effect Detail is set to *High*
- Ensure Shader Detail is set to *Very High*
- Ensure Boost Player Contrast is set to *Enabled*
- Ensure Multicore Rendering is set to *Enabled*
- Ensure Multisampling Anti-Aliasing Mode is set to *8x MSAA*
- Ensure FXAA Anti-Aliasing is set to *Disabled*
- Ensure Texture Filtering Mode is set to *Trilinear*
- Ensure Wait for Vertical Sync is set to *Disabled*
- Ensure Motion Blur is set to *Disabled*
- Ensure Triple Monitor Mode is set to *Disabled*
- Ensure Use Uber Shadows is set to *Enabled*

Click *Apply Changes*, then the *power button* at the bottom left of the screen. Click *Quit* to exit the game, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/37dfBoFAfwim9URQ-embedded-image-zo81azad.png)</span></span>

[![video settings 1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/zms4iW0Sw7dgY93A-video-settings-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/zms4iW0Sw7dgY93A-video-settings-1.png)

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6TUmerYnwOhe9hWj-embedded-image-fmrovajb.png)</span></span>

## 2560x1440

### Games-1440

Launch the game and go to the settings menu.

#### Game

- Ensure Enable Developer Console is set to *Yes*

#### Video

- Ensure Resolution is set to *2560x1440*
- Ensure display mode is set to *Fullscreen*
- Ensure Laptop Power Savings is set to *Disabled*
- Ensure Global Shadow Quality is set to *High*
- Ensure Model / Texture Detail is set to *High*
- Ensure Texture Streaming is set to *Disabled*
- Ensure Effect Detail is set to *High*
- Ensure Shader Detail is set to *Very High*
- Ensure Boost Player Contrast is set to *Enabled*
- Ensure Multicore Rendering is set to *Enabled*
- Ensure Multisampling Anti-Aliasing Mode is set to *8x MSAA*
- Ensure FXAA Anti-Aliasing is set to *Disabled*
- Ensure Texture Filtering Mode is set to *Trilinear*
- Ensure Wait for Vertical Sync is set to *Disabled*
- Ensure Motion Blur is set to *Disabled*
- Ensure Triple Monitor Mode is set to *Disabled*
- Ensure Use Uber Shadows is set to *Enabled*

Click *Apply Changes*, then the *power button* at the bottom left of the screen. Click *Quit* to exit the game, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/37dfBoFAfwim9URQ-embedded-image-zo81azad.png)</span></span>

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/9aunDXKS3zTim5Ow-embedded-image-5nu0lnaa.png)</span></span>

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6TUmerYnwOhe9hWj-embedded-image-fmrovajb.png)</span></span>


## 3840x2160

### Games-2160

Launch the game and go to the settings menu.

#### Game

- Ensure Enable Developer Console is set to *Yes*

#### Video

- Ensure Resolution is set to *3840x2160*
- Ensure display mode is set to *Fullscreen*
- Ensure Laptop Power Savings is set to *Disabled*
- Ensure Global Shadow Quality is set to *High*
- Ensure Model / Texture Detail is set to *High*
- Ensure Texture Streaming is set to *Disabled*
- Ensure Effect Detail is set to *High*
- Ensure Shader Detail is set to *Very High*
- Ensure Boost Player Contrast is set to *Enabled*
- Ensure Multicore Rendering is set to *Enabled*
- Ensure Multisampling Anti-Aliasing Mode is set to *8x MSAA*
- Ensure FXAA Anti-Aliasing is set to *Disabled*
- Ensure Texture Filtering Mode is set to *Trilinear*
- Ensure Wait for Vertical Sync is set to *Disabled*
- Ensure Motion Blur is set to *Disabled*
- Ensure Triple Monitor Mode is set to *Disabled*
- Ensure Use Uber Shadows is set to *Enabled*

Click *Apply Changes*, then the *power button* at the bottom left of the screen. Click *Quit* to exit the game, then run via Markbench. Results should be uploaded via the Upload tab after all runs have completed successfully.

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/37dfBoFAfwim9URQ-embedded-image-zo81azad.png)</span></span>

[![video settings 1.png](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/scaled-1680-/vRLhXwj2eCNXbrkL-video-settings-1.png)](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-07/vRLhXwj2eCNXbrkL-video-settings-1.png)

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 351px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/6TUmerYnwOhe9hWj-embedded-image-fmrovajb.png)</span></span>

## <span style="font-size: 20pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">Trimming Grafana</span>

<span style="font-size: 11pt; font-family: Arial; color: #000000; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"><span style="border: none; display: inline-block; overflow: hidden; width: 624px; height: 123px;">![](https://wiki.floatplaneinfra.com/uploads/images/gallery/2023-05/X4q7FVBYnJGyxYaX-embedded-image-onoy6lfe.png)</span></span>

<span style="font-weight: normal;">  
  
</span>