📺 TV TIME (Offline Video Viewer)
An interactive, retro-style offline TV application built with Python, Tkinter, and Pygame. It replicates a vintage television experience complete with simulated static backgrounds, channel surfing, custom color themes, and media playback controls.

✨ Features
Retro TV Interface: Features a nostalgic television static background animation with adjustable intensity.

Channel Surfing: Easily switch between different video files using the Next / Prev buttons, random TV mode, or keyboard shortcuts.

Universal File Selector & Drag-and-Drop: Open local .mp4 video files instantly via the built-in file picker button or drag-and-drop support.

Customization Settings: Change background color themes (Royal Purple, Midnight Blue, Cyberpunk, etc.) and fine-tune static transparency.

Advanced Playback Controls: Includes play/pause, looping, speed adjustment (0.5x to 2.0x), volume control, muting, and a Picture-in-Picture (PiP) mode.

Multi-Language Support: Localized interface options including English, Spanish, French, German, Turkish, Portuguese, Italian, Russian, Chinese, and Japanese.

🛠️ Requirements & Dependencies
Make sure you have Python installed along with the required libraries. You can install the core dependencies via pip:

Bash
pip install opencv-python pillow pygame numpy tkinterdnd2 moviepy
Note: tkinterdnd2 requires desktop window hooks and is designed for desktop execution.

🚀 How to Run
Clone or download this repository to your local machine.

Place your .mp4 video files and required audio assets (.wav) in the project directory.

Run the main script:

Bash
python tv_time_app.py
⌨️ Keyboard Shortcuts
Space: Pause / Resume

ESC: Stop / Exit video player

Left / Right Arrow: Seek backward / forward (5 seconds)

M: Mute / Unmute audio

F11: Toggle Fullscreen

📝 License
This project is open-source and available under the MIT License.
