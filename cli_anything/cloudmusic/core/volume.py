"""Volume control for NetEase CloudMusic."""

from typing import Optional
from ..utils import CloudMusicBackend


class VolumeController:
    """Controls system volume via media keys."""

    # Note: We're sending volume keys which affect system volume.
    # This is what NetEase CloudMusic uses when global shortcuts is enabled.

    DEFAULT_DELTA = 10

    def __init__(self, backend: CloudMusicBackend):
        self.backend = backend

    def is_running(self) -> bool:
        """Check if CloudMusic is running."""
        return self.backend.is_running()

    def up(self, delta: int = DEFAULT_DELTA) -> bool:
        """Increase volume.

        Args:
            delta: Number of steps to increase (each step is about 4% on Windows).

        Returns:
            True if commands sent successfully.
        """
        if not self.is_running():
            return False
        for _ in range(delta):
            self.backend.send_volume_up()
        return True

    def down(self, delta: int = DEFAULT_DELTA) -> bool:
        """Decrease volume.

        Args:
            delta: Number of steps to decrease.

        Returns:
            True if commands sent successfully.
        """
        if not self.is_running():
            return False
        for _ in range(delta):
            self.backend.send_volume_down()
        return True

    def toggle_mute(self) -> bool:
        """Toggle mute state.

        Returns:
            True if command sent successfully.
        """
        if not self.is_running():
            return False
        self.backend.send_volume_mute()
        return True
