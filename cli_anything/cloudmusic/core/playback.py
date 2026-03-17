"""Playback control commands for NetEase CloudMusic."""

from ..utils import CloudMusicBackend


class PlaybackController:
    """Controls playback state."""

    def __init__(self, backend: CloudMusicBackend):
        self.backend = backend

    def is_running(self) -> bool:
        """Check if CloudMusic is running."""
        return self.backend.is_running()

    def play(self) -> bool:
        """Start or resume playback.

        **Known limitation:** Since we can't get current playback state from CloudMusic,
        this just sends a play/pause toggle. If it's already playing, this will pause it.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        # If paused, send play/pause to resume
        self.backend.send_play_pause()
        return True

    def pause(self) -> bool:
        """Pause current playback.

        **Known limitation:** Since we can't get current playback state from CloudMusic,
        this just sends a play/pause toggle. If it's already paused, this will resume it.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        # If playing, send play/pause to pause
        self.backend.send_play_pause()
        return True

    def toggle(self) -> bool:
        """Toggle play/pause.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        self.backend.send_play_pause()
        return True

    def next(self) -> bool:
        """Skip to next track.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        self.backend.send_next_track()
        return True

    def previous(self) -> bool:
        """Go to previous track.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        self.backend.send_previous_track()
        return True

    def like(self) -> bool:
        """Like/favorite the current track (uses Ctrl+S shortcut).

        This toggles the favorite state of the current track in NetEase CloudMusic.

        Returns:
            True if command sent successfully, False if app not running.
        """
        if not self.is_running():
            return False
        self.backend.send_like_shortcut()
        return True
