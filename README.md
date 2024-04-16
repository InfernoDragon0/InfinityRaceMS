# Infinity Race (Maplestory)

Automatically complete the Infinity Race PvP minigame in Maplestory! A GPU with CUDA compatiblity is necessary for high performance detection. If you are running it via a CPU, it will be much slower.

### TODO
- This is a work in progress. Will be considered completed once this TODO note is removed.

### Installation
- Tested on Python 3.11
- Install the requirements.txt
- (Optional, Recommended) If running on a GPU, go to https://pytorch.org/ and select your configuration to install.
- If you already had the CPU version of pyTorch and want to convert to GPU, you should `pip uninstall torch, torchaudio and torchvision` first to avoid conflicts

### Configuration
- Configure your `crouch` and `jump` keys as required
- You can enable `debug` to see what is happening in openCV

### Model
- A simple model `infinityrace.pt` based on the `yolov8m.pt` model is trained to detect the stones and automatically perform actions based on the proximity to the player.