"""Window detector for parsing track information from NetEase CloudMusic window title.
"""

import re
from typing import Optional, Tuple

from .cloudmusic_backend import CloudMusicBackend

TrackInfo = Tuple[Optional[str], Optional[str]]


class WindowDetector:
    """Detects and parses current track information from window title.

    Typical window title format: "{title} - {artist} - CloudMusic"
    """

    # Regex patterns to match various title formats
    # Pattern 1: "Title - Artist - CloudMusic"
    # Pattern 2: "Title - Artist - Album - CloudMusic"
    # Some versions put artist first occasionally
    _PATTERNS = [
        re.compile(r"^(.*?)\s*-\s*(.*?)\s*-\s*CloudMusic$"),
        re.compile(r"^(.*?)\s*-\s*CloudMusic$"),
    ]

    def __init__(self, backend: CloudMusicBackend):
        self.backend = backend

    def parse_title(self, title: str) -> TrackInfo:
        """Parse window title to extract (title, artist).

        Returns:
            (title, artist) tuple, either or both can be None if parsing fails.
        """
        if not title:
            return (None, None)

        # Remove " - CloudMusic" suffix
        title = title.rstrip()
        if title.endswith(" - CloudMusic"):
            title = title[:-12].rstrip()

        # Is there are multiple " - " separators
        parts = title.split(" - ")

        if len(parts) >= 2:
            # Common case: title - artist
            title_part = " - ".join(parts[:-1])
            artist_part = parts[-1]
            return (title_part.strip(), artist_part.strip())
        elif len(parts) == 1:
            # Only song name only available
            return (parts[0].strip(), None)

        return (None, None)

    def get_current_track(self) -> TrackInfo:
        """Get current track info from the window title.

        Returns:
            (title, artist) tuple, (None, None) if not running or not found.
        """
        if not self.backend.is_running():
            return (None, None)

        title = self.backend.get_window_title()
        if not title:
            return (None, None)

        return self.parse_title(title)

    def get_playback_state(self) -> Optional[bool]:
        """Get playback state from window.

        Note: Since we can't easily get this from window title alone,
        this always returns None (unknown) unless we can detect it.
        Only reliable indicator is whether the app is running or not.

        For most cases you can check if app is running.

        Returns:
            True if playing, False if paused, None if unknown
        """
        # Currently we can't detect this from the window title
        # So always returns None
        # Future: Could use pixel scanning from play/pause button
        # But that requires more complex automation
        return None

    def is_running(self) -> bool:
        """Check if CloudMusic is running."""
        return self.backend.is_running()
