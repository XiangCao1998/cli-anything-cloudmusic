# NetEase CloudMusic Analysis

## Installation

**Windows Path:**
```
D:\Program Files\NetEase\CloudMusic\cloudmusic.exe
```

**WSL Path:**
```
/mnt/d/Program Files/NetEase/CloudMusic/cloudmusic.exe
```

## Version

Installed version: Latest as of 2025.

## Control Mechanisms

### Global Media Keys
NetEase CloudMusic responds to global media keyboard shortcuts:
- `VK_MEDIA_PLAY_PAUSE` (0xB3) - Toggle play/pause
- `VK_MEDIA_NEXT_TRACK` (0xB0) - Next track
- `VK_MEDIA_PREV_TRACK` (0xB1) - Previous track
- `VK_VOLUME_UP` (0xAF) - Increase volume
- `VK_VOLUME_DOWN` (0xAE) - Decrease volume
- `VK_VOLUME_MUTE` (0xAD) - Toggle mute

These can be sent via Windows `SendInput` API.

### Window Title Format

The main window title typically follows the format:
```
{Title} - {Artist} - CloudMusic
```

Examples:
- `晴天 - 周杰伦 - CloudMusic`
- `七里香 - 周杰伦 - CloudMusic`

This allows us to extract current track information without OCR or deeper UI automation.

### Window Class

Window class name: `Chrome_WidgetWin_0` (Electron app).

## Architecture Notes

- Based on Electron/CEF
- Closed-source, no public API
- No native CLI interface
- Must use Windows automation for control

## Supported Features for Basic CLI

✅ Play/pause toggle via media key
✅ Next/previous track via media keys
✅ Volume up/down/mute via media keys
✅ Extract current track from window title
✅ Launch/quit application control
✅ Show/hide window

❌ Advanced search (requires UI automation - out of scope)
❌ Playlist management (requires UI automation - out of scope)
❌ Seeking to position (no simple media key - out of scope)
❌ Lyrics retrieval (no simple method - out of scope)
