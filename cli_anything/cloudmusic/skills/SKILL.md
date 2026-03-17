---
name: cli-anything-cloudmusic
description: Control NetEase CloudMusic (网易云音乐) via command-line
software: NetEase CloudMusic
type: cli-anything
commands:
  - cli-anything-cloudmusic
keywords:
  - music
  - player
  - cloudmusic
  - 网易云音乐
  - playback
  - audio
license: MIT
---

# CLI-Anything: NetEase CloudMusic

Command-line interface for controlling **NetEase CloudMusic (网易云音乐)** on Windows via the CLI-Anything framework.

## Features

- ✨ **Playback Control**: play, pause, toggle, next, previous
- 🔊 **Volume Control**: volume up, volume down, mute toggle
- ℹ️ **Track Info**: Get current track title and artist
- 🚀 **App Control**: launch, quit, show, hide window
- 🔄 **REPL Mode**: Interactive mode with autocomplete
- 🤖 **JSON Output**: Machine-readable output for AI agents

## Installation

```bash
pip install cli-anything-cloudmusic
```

Or install from source:

```bash
cd cloudmusic
pip install -e .
```

## Usage

```bash
# Launch the app
cli-anything-cloudmusic launch

# Get current track
cli-anything-cloudmusic current

# Toggle play/pause
cli-anything-cloudmusic toggle

# Next track
cli-anything-cloudmusic next

# Increase volume by 10
cli-anything-cloudmusic volume up 10

# Start interactive REPL
cli-anything-cloudmusic

# JSON output for AI (--json goes before the command)
cli-anything-cloudmusic --json current
```

## Available Commands

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
| `volume` | Get or adjust volume |
| `mute` | Toggle mute |
| `current` | Show current track |
| `status` | Show playback status |
| `like` | Toggle like/favorite on current track |
| `detect` | Auto-detect CloudMusic installation |
| `config <path>` | Save custom path to cloudmusic.exe |

## Requirements

- Windows 10/11
- NetEase CloudMusic installed
- Python 3.8+ (Windows)
- pywin32, click, psutil, prompt_toolkit

## For AI Agents

### Quick Start for AI

When the user asks to play music/control NetEase CloudMusic:

1. **First check if it's installed and detected**:
   ```bash
   cli-anything-cloudmusic --json detect
   ```
   If `success: false`, ask the user for the path to `cloudmusic.exe` and configure it:
   ```bash
   cli-anything-cloudmusic config "C:\Program Files\NetEase\CloudMusic\cloudmusic.exe"
   ```

2. **Launch if not running**:
   ```bash
   cli-anything-cloudmusic launch
   ```

3. **Control playback**:
   ```bash
   cli-anything-cloudmusic play      # Start playback
   cli-anything-cloudmusic next     # Next track
   cli-anything-cloudmusic pause    # Pause
   ```

4. **Always use `--json` for machine-readable output**:
   ```bash
   cli-anything-cloudmusic --json current
   ```

Output example:
```json
{
  "success": true,
  "title": "晴天",
  "artist": "周杰伦",
  "running": true
}
```

This makes it easy for AI agents to parse the output and act on results.

All commands support the `--json` flag that outputs structured JSON. **Note:** `--json` must be placed before the command.

## Auto-Discovery

The tool automatically tries to find CloudMusic in this order:

1. Custom configured path from `~/.config/cli-anything-cloudmusic/path.txt`
2. Windows Registry search (uninstall information)
3. `where.exe` search
4. Common default installation paths
5. Search Program Files on all common drives (C:, D:, E:, F:)

If auto-discovery fails, just use `config` command to set a custom path - it will be saved persistently.

## Running from WSL (Windows Subsystem for Linux)

If you're using WSL, you need to use the **Windows version of Python** for the Windows API to work:

```bash
# Add Windows Python to your WSL PATH in ~/.bashrc
export PATH="$PATH:/mnt/c/Users/YOUR_NAME/AppData/Local/Programs/Python/Python3x/Scripts"

# Install using Windows pip
/mnt/c/Users/YOUR_NAME/AppData/Local/Programs/Python/Python3x/python.exe -m pip install -e .

# Run commands directly
cli-anything-cloudmusic launch
cli-anything-cloudmusic play
```
