<img src="images/labs_icon.png" alt="Logo" width="100" height="56" />
<h1>Markbench Test Harnesses</h1>

<!-- omit in toc -->
## About The Project
Welcome to the official MarkBench testing platform developed by the LTT Labs team. MarkBench serves as the orchestration and data collection framework, while the tests themselves form the core of this process. The tests featured in this repository are actively employed to generate the data showcased in LTT (Linus Tech Tips) videos. We've made the code available here, allowing anyone to execute the very same tests that we use. It's worth noting that you do not require MarkBench to execute the tests provided within this project.

### Project versions
The versions of tests that are available here are taken from snapshots of our private working repository where we maintain and update existing tests as well as develop and add new tests. We are making the effort to provide new versions of our code to the public at least once a quarter (i.e. every three months). However, we may occasionally release versions more often than this, should we have changes that we feel are worth sharing sooner rather than later. Depending on the changes we have made during the time between release versions, the differences in versions may vary in the amount and significance of changes made.


<!-- omit in toc -->
## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
    - [Python 3.10+](#python-310)
    - [Poetry](#poetry)
      - [Downloading dependencies](#downloading-dependencies)
- [A test and its harness](#a-test-and-its-harness)
- [Creating a test harness](#creating-a-test-harness)
- [Tools in the toolbox](#tools-in-the-toolbox)
  - [Keras OCR](#keras-ocr)
  - [Keyboard and Mouse Input](#keyboard-and-mouse-input)
- [License](#license)

## Getting Started
Configuring your system to execute these tests is straightforward; you'll only need Python, Poetry, and git. However, it's important to note that some of the tests in this repository may necessitate additional services or specific applications to be installed. For instance, if you intend to run the game tests, you will need to possess a valid copy of the respective game title.

### Prerequisites

#### Python 3.10+
Most of the test harnesses are written in Python, which you will need on your system. We use Python 3.11 on our test benches, but should work on versions since 3.10.

<!-- omit in toc -->
##### Installation
We recommend you install python from the [official downloads page](https://www.python.org/downloads/) and not the Windows Store.

#### Poetry
This project uses [Poetry](https://python-poetry.org/docs/) for dependency management. 

<!-- omit in toc -->
##### Installation
Open a powershell terminal and execute the following command to download and execute the install script.
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
After installation you will want to add poetry to the path. On Windows this path to add is `%APPDATA%\Python\Scripts`. Test that poetry is working by executing `poetry --version`, a version number should be returned, not an error.

##### Downloading dependencies
1. Open a terminal in the root directory.
2. Execute `poetry install`

Poetry installs dependencies into virtual environments. You can read more about [managing poetry environments here.](https://python-poetry.org/docs/managing-environments/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- omit in toc -->
### Running your first test
Once you've successfully installed Python and Poetry, it's time to kick off our initial test. We'll begin by launching MSI Kombustor, which serves as our primary choice for testing and exploring new MarkBench functionalities. MSI Kombustor provides an excellent starting point for acquainting yourself with our test harnesses, as it doesn't necessitate any additional automation tools from our toolkit.

Let's take a look at the folder structure

- msikombuster (dir)
  - run (dir)
  - manifest.yaml
  - msikombuster.py
  - README.md

When we mention "test harness," we are specifically referring to the entire directory and its contents. Within this directory, we anticipate, at the very least, the presence of an executable file that follows the guideline of returning either 1 or 0 to signify the completion status. Additionally, the manifest.yaml serves as metadata that allows MarkBench to identify it; however, for now, we can disregard it.

The run directory, on the other hand, is the designated location for all outputs, including log files or screenshots. While it's not an absolute requirement, it has been the prevailing convention thus far.

1. First [install MSI Kombustor](https://geeks3d.com/furmark/kombustor/) using the default install location and options.

2. Second open a Powershell terminal and navigate to the root of the msikombustor directory.

<img src="images/run_your_first_test_image1.png" alt="Logo" width="500" height="180" />

3. From this directory run the command 
```powershell
python .\msikombuster.py --test vkfurrytorus --resolution "1080,1920" -b true
```

Executing this command initiates MSI Kombustor in benchmark mode, specifically launching the (VK) FurMark-Donut test at a resolution of 1920 x 1080. After the benchmark run concludes, you'll find the log and any captured assets stored within the **msikombuster/run** directory.

It's important to note that the arguments required for each harness may vary. To ensure smooth test execution, consult the README of each harness, which provides detailed instructions on any unique requirements for running that specific test.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## A test and its harness
MarkBench has the capability to accommodate any test that can be carried out on a Windows system and concludes with a success code of 0 or a failure code of 1. For MarkBench to recognize a test harness as automatable, it must include a manifest.yaml file containing essential metadata about the harness.

The test harness is responsible for:
1. Setup
2. Execution
3. Gathering of assets
4. Cleanup

## Creating a test harness
Let's create a harness for the test FurMark.

```python
import os.path
import sys

DEFAULT_FURMARK_DIR = "C:\\Program Files (x86)\\Geeks3D\\Benchmarks\\FurMark"
EXECUTABLE = "FurMark.exe"
ABS_EXECUTABLE_PATH = os.path.join(DEFAULT_FURMARK_DIR, EXECUTABLE)

if os.path.isfile(ABS_EXECUTABLE_PATH) is False:
    raise ValueError('No FurMark installation detected! Default installation expected to be present on the system.')

# omit the first arg which is the script name
args = sys.argv[1:]
command = f'"{ABS_EXECUTABLE_PATH}" '
for arg in args:
    command += arg + ' '

command = command.rstrip()
os.system(command)
```
This is a very simple harness which takes in the arguments passed from the commandline and then executes the `FurMark.exe` test. A test harness can vary wildly in complexity depending on the test the harness is implementing. A canned game benchmark might require use of libraries like PyAutoGui to navigate around a game menu, or edit registry to setup configuration.

Harness entrypoints and any supporting files should live in a named directory in the root harness directory.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Tools in the toolbox

### Keras OCR

We employ a deployment of [Keras OCR](https://github.com/faustomorales/keras-ocr) integrated into an HTTP API to assist in navigating game menus. This service accepts an image and a designated target word, and in return, it provides the coordinates of the word's location within the image. If the word cannot be located, it returns a "false" response.

For detailed instructions on setting up this Keras Service locally, please refer to our [Keras Service repository linked here](https://github.com/LTTLabsOSS/keras-ocr-service).

> Please note that although a CUDA-capable GPU is not mandatory, it's worth mentioning that certain games may not function correctly due to slower response times when this hardware is absent.

### Keyboard and Mouse Input

For keyboard and mouse input, we employ two distinct methods. The first method involves using Virtual Key Codes (VKs) with the deprecated Win32 functions mouse_event() and keybd_event(). The second method utilizes Send Input. Specifically, [PyAutoGui](https://pyautogui.readthedocs.io/en/latest/) implements the first approach, while [PyDirectInput](https://pypi.org/project/PyDirectInput/) implements the second.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the GNU GENERAL PUBLIC LICENSE Version 3. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
