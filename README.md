# Infinity Race (Maplestory)
<img width="952" alt="aiscore" src="https://github.com/InfernoDragon0/InfinityRaceMS/assets/1367130/cb80edcd-6629-4a89-83a0-9fe7eda2c5ff">

Automatically complete the Infinity Race PvP minigame in Maplestory! A GPU with CUDA compatiblity is necessary for high performance detection. If you are running it via a CPU, it will be much slower.

### Branches
- There are 3 branches, `main`, `alternate`, `playsafe`.
- Main branch uses time based delays to perform actions, and may sometimes not jump or crouch on time at the faster rounds.
- Alternate branch holds to perform actions, and may sometimes uncrouch too early and break head on high stones.
- Playsafe branch does not have delays, and runs at full speed. It will attempt to crouch and jump at the safest times and remain crouched until the next action is taken. The tradeoff for this branch will be the loss of points between multiple high stones, and you will need to manually uncrouch for fever time if the last stone was a high stone.

### Installation
- Tested on Python 3.11
- Install the requirements.txt
- (Optional, Recommended) If running on a GPU, go to https://pytorch.org/ and select your configuration to install.
- If you already had the CPU version of pyTorch and want to convert to GPU, you should `pip uninstall torch, torchaudio and torchvision` first to avoid conflicts

### Configuration
- Configure your `h` and `w` variables to your window size. `h` can be anything from the full size to half the size + 100, reducing `h` improves performance.
- You can enable `debug` to see what is happening in openCV

### Model
- A simple model `infinityrace.pt` based on the `yolov8m.pt` model is trained to detect the stones and automatically perform actions based on the proximity to the player.
