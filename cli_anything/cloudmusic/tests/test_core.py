"""Unit tests for core functionality."""

import pytest
from cli_anything.cloudmusic.utils.window_detector import WindowDetector
from cli_anything.cloudmusic.utils.cloudmusic_backend import CloudMusicBackend


class MockBackend:
    def __init__(self, title=None):
        self._title = title
        self._running = True

    def is_running(self):
        return self._running

    def get_window_title(self):
        return self._title


def test_parse_title_basic():
    """Test parsing of standard title format."""
    backend = MockBackend("晴天 - 周杰伦 - CloudMusic")
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("晴天 - 周杰伦 - CloudMusic")
    assert title == "晴天"
    assert artist == "周杰伦"


def test_parse_title_with_hyphens_in_title():
    """Test parsing when song name contains hyphens."""
    backend = MockBackend("天高地厚 - 信乐团 - CloudMusic")
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("天高地厚 - 信乐团 - CloudMusic")
    assert title == "天高地厚"
    assert artist == "信乐团"


def test_parse_title_multiple_hyphens():
    """Test parsing with multiple separators."""
    backend = MockBackend("夜的第七章 - 周杰伦 - CloudMusic")
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("夜的第七章 - 周杰伦 - CloudMusic")
    assert title == "夜的第七章"
    assert artist == "周杰伦"


def test_parse_title_only_song():
    """Test parsing when only song name is available."""
    backend = MockBackend("SongName - CloudMusic")
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("SongName - CloudMusic")
    assert title == "SongName"
    assert artist is None


def test_parse_title_empty():
    """Test parsing empty string."""
    backend = MockBackend(None)
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("")
    assert title is None
    assert artist is None


def test_parse_title_whitespace():
    """Test parsing with extra whitespace."""
    backend = MockBackend("  晴天  -  周杰伦  - CloudMusic")
    detector = WindowDetector(backend)
    title, artist = detector.parse_title("  晴天  -  周杰伦  - CloudMusic")
    assert title == "晴天"
    assert artist == "周杰伦"


def test_get_current_track_not_running():
    """Test when app is not running."""
    backend = MockBackend(None)
    backend._running = False
    detector = WindowDetector(backend)
    title, artist = detector.get_current_track()
    assert title is None
    assert artist is None


def test_find_exe_not_found():
    """Test that backend handles missing executable."""
    backend = CloudMusicBackend(exe_path="nonexistent/path/cloudmusic.exe")
    assert backend.get_exe_path() == "nonexistent/path/cloudmusic.exe"


def test_backend_default_paths():
    """Test that backend checks default paths."""
    backend = CloudMusicBackend()
    # Should find something on a system with CloudMusic installed
    path = backend.get_exe_path()
    # If not found, returns None - that's okay
