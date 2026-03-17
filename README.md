# CLI-Anything CloudMusic

[![CI](https://github.com/XiangCao1998/cli-anything-cloudmusic/actions/workflows/ci.yml/badge.svg)](https://github.com/XiangCao1998/cli-anything-cloudmusic/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cli-anything-cloudmusic.svg)](https://pypi.org/project/cli-anything-cloudmusic/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Command-line interface for **NetEase CloudMusic (网易云音乐)** on Windows.

Control your music player from the command line or let AI agents control it.

Perfect for AI assistants like Claude Code to control your music playback via natural language.

## Features

- ✨ **Playback Control**: play, pause, toggle, next, previous, like (favorite)
- 🔊 **Volume Control**: volume up, volume down, volume set to %, mute toggle
- 🎵 **Track Info**: Get current track title and artist
- 🚀 **App Control**: launch, quit, show, hide window
- 🔧 **Auto-discovery**: Automatically finds CloudMusic installation
- ⚙️ **Configurable**: Supports custom installation path
- 🔄 **REPL Mode**: Interactive mode with autocomplete
- 🤖 **JSON Output**: Machine-readable output for AI agents
- 🪟 **WSL Support**: Works perfectly from Windows Subsystem for Linux

## Installation

### Prerequisites
- Windows 10/11
- NetEase CloudMusic already installed (auto-discovers from default locations)
- Python 3.8+ (Windows version, **not WSL Python**)

### Install via git (recommended for development)

```bash
git clone https://github.com/XiangCao1998/cli-anything-cloudmusic.git
cd cli-anything-cloudmusic
python -m pip install -e .
```

### Install via pip (once published)

```bash
pip install cli-anything-cloudmusic
```

### Install for WSL (Windows Subsystem for Linux)

If you're using WSL and want to run commands from the WSL terminal:

1. Install Python for Windows first (from [python.org](https://www.python.org/downloads/windows/))
2. Add Windows Python/Scripts to your WSL `PATH` in `~/.bashrc`:
```bash
export PATH="$PATH:/mnt/c/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python312"
export PATH="$PATH:/mnt/c/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python312/Scripts"
```
3. Reload shell and install:
```bash
source ~/.bashrc
git clone https://github.com/XiangCao1998/cli-anything-cloudmusic.git
cd cli-anything-cloudmusic
python -m pip install -e .
```

Now you can run commands directly from WSL:
```bash
cli-anything-cloudmusic play
cli-anything-cloudmusic next
```

## Usage

### Commands

**Application Control:**
```bash
cli-anything-cloudmusic launch    # Launch NetEase CloudMusic
cli-anything-cloudmusic quit      # Close the application
cli-anything-cloudmusic show      # Bring window to foreground
cli-anything-cloudmusic hide      # Minimize to system tray
```

**Playback Control:**
```bash
cli-anything-cloudmusic play       # Start/resume playback
cli-anything-cloudmusic pause      # Pause playback
cli-anything-cloudmusic toggle     # Toggle play/pause
cli-anything-cloudmusic next       # Next track
cli-anything-cloudmusic previous   # Previous track
cli-anything-cloudmusic like       # Toggle like/favorite on current track
```

**Volume Control:**
```bash
cli-anything-cloudmusic volume              # Show current volume
cli-anything-cloudmusic volume set 50      # Set volume to 50%
cli-anything-cloudmusic volume up 10        # Increase volume by 10
cli-anything-cloudmusic volume down 5       # Decrease volume by 5
cli-anything-cloudmusic mute                # Toggle mute
```

**Track Information:**
```bash
cli-anything-cloudmusic status    # Get playback status
cli-anything-cloudmusic current    # Get current track info
```

**Configuration & Discovery:**
```bash
cli-anything-cloudmusic detect    # Auto-detect CloudMusic installation
cli-anything-cloudmusic config <path>  # Save custom installation path
```

**JSON Output (for AI agents):**
```bash
cli-anything-cloudmusic --json current
# Output: {"title": "晴天", "artist": "周杰伦", "running": true, "playing": true}
```

**Interactive REPL:**
```bash
cli-anything-cloudmusic
# Starts interactive mode with autocomplete
```

## Running from WSL

If you're using Windows Subsystem for Linux (WSL), you need to run the Windows Python:

```bash
# Add Windows Python to WSL PATH in ~/.bashrc
export PATH="$PATH:/mnt/c/Users/YOUR_NAME/AppData/Local/Programs/Python/Python3x"

# Run directly
cli-anything-cloudmusic current
```

## Usage for AI Agents

All commands support the `--json` flag for machine-readable output that AI can easily parse:

```bash
cli-anything-cloudmusic --json current
```

Example output:
```json
{
  "success": true,
  "title": "晴天",
  "artist": "周杰伦",
  "running": true
}
```

**Available Commands:**

| Command | Description |
|---------|-------------|
| `launch` | Launch NetEase CloudMusic |
| `quit` | Close the application |
| `show` | Bring window to foreground |
| `hide` | Minimize to system tray |
| `play` | Start/resume playback |
| `pause` | Pause playback |
| `toggle` | Toggle play/pause |
| `next` | Skip to next track |
| `previous` | Go to previous track |
| `like` | Toggle like/favorite on current track |
| `volume up [N]` | Increase volume by N (default: 10) |
| `volume down [N]` | Decrease volume by N (default: 10) |
| `volume set <0-100>` | Set volume to specific percentage |
| `mute` | Toggle mute |
| `current` | Show current track information |
| `status` | Show playback status |
| `detect` | Auto-detect CloudMusic installation |
| `config <path>` | Save custom installation path |

## How It Works

This tool uses Windows API to simulate media key presses (play/pause/next/etc.) which works regardless of whether the CloudMusic window is focused or in the background.

Process detection handles the WSL UNC path issue that caused problems with older versions. CloudMusic executable is auto-discovered from common install locations.

## Troubleshooting

### Command says "success" but nothing happens
- Make sure you are using **Windows Python**, not WSL Python. The Windows API needs to be called from Windows.
- If using WSL, you must call the Windows Python interpreter, not the WSL Python.

### "CloudMusic is not running" even though it's open
- The detection should work now. If it still fails, try: `cli-anything-cloudmusic launch` to restart it.

### Can't get title/artist
- Title extraction relies on window title. Some versions of CloudMusic may not expose this. Status detection (running/not running) should always work.

## License

MIT
