"""Track information retrieval for NetEase CloudMusic."""

from dataclasses import dataclass
from typing import Optional

from ..utils import CloudMusicBackend, WindowDetector


@dataclass
class CurrentTrack:
    """Information about the currently playing track."""
    title: Optional[str] = None
    artist: Optional[str] = None
    running: bool = False

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "running": self.running,
        }


class TrackInfoRetriever:
    """Retrieves current track information from window title."""

    def __init__(self, backend: CloudMusicBackend, detector: WindowDetector):
        self.backend = backend
        self.detector = detector

    def get_current(self) -> CurrentTrack:
        """Get current track information.

        Returns:
            CurrentTrack object with title and artist.
            If app is not running, returns empty object.
        """
        track = CurrentTrack()
        if not self.backend.is_running():
            return track

        title, artist = self.detector.get_current_track()
        track.title = title
        track.artist = artist
        track.running = True
        return track

    def get_status(self) -> dict:
        """Get playback status.

        Returns:
            Status dict with running and playing info.
        """
        current = self.get_current()
        return {
            "running": current.running,
            "playing": self.detector.get_playback_state(),
            "title": current.title,
            "artist": current.artist,
        }
