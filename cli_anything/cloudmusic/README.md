# CLI-Anything CloudMusic

Command-line interface for **NetEase CloudMusic (网易云音乐)** on Windows.

Control your music player from the command line or let AI agents control it.

## Installation

### Prerequisites
- Windows 10/11
- NetEase CloudMusic already installed at `C:\Program Files\NetEase\CloudMusic\cloudmusic.exe` or `D:\Program Files\NetEase\CloudMusic\cloudmusic.exe`
- Python 3.8+ (Windows version, not WSL Python)

### Install from source
```bash
cd cloudmusic
pip install -e .
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

**JSON Output (for AI agents):**
```bash
cli-anything-cloudmusic current --json
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

## License

MIT
