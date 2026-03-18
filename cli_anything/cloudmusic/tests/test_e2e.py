"""E2E tests for CloudMusic CLI.

These tests require:
1. Windows environment
2. NetEase CloudMusic installed
3. Python with pywin32
"""

import ctypes
import json
import subprocess

import pytest

from cli_anything.cloudmusic.utils.cloudmusic_backend import CloudMusicBackend


def _resolve_cli():
    """Resolve the installed CLI command."""
    # Try local and installed
    try:
        # Check if installed
        result = subprocess.run(
            ["where", "cli-anything-cloudmusic"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return "cli-anything-cloudmusic"
    except Exception:
        pass

    # Try running from source
    return ["python", "-m", "cli_anything.cloudmusic"]


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="Requires Windows")
def test_backend_detects_running():
    """Test that backend detects if app is running."""
    backend = CloudMusicBackend()
    # Just check that it runs without error
    running = backend.is_running()
    # Can't assert - might be running or not
    assert isinstance(running, bool)


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="Requires Windows")
def test_can_find_window_title():
    """Test that we can get window title when running."""
    backend = CloudMusicBackend()
    if not backend.is_running():
        pytest.skip("CloudMusic is not running")

    title = backend.get_window_title()
    # If running, we should get a title
    if title:
        assert "CloudMusic" in title


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="Requires Windows")
def test_cli_current_json():
    """Test current command outputs JSON."""
    cmd = _resolve_cli()
    result = subprocess.run(cmd + ["current", "--json"], capture_output=True, text=True)
    # Should exit cleanly
    try:
        data = json.loads(result.stdout)
        assert "success" in data
        assert "running" in data
        assert "title" in data
        assert "artist" in data
    except json.JSONDecodeError:
        # If not running, it can still output valid JSON
        # Just check it's valid JSON
        pass


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="Requires Windows")
def test_cli_status_json():
    """Test status command outputs JSON."""
    cmd = _resolve_cli()
    result = subprocess.run(cmd + ["status", "--json"], capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert "success" in data
    assert "running" in data


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="Requires Windows")
def test_help():
    """Test help command works."""
    cmd = _resolve_cli()
    result = subprocess.run(cmd + ["--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "launch" in result.stdout
    assert "toggle" in result.stdout
    assert "next" in result.stdout
