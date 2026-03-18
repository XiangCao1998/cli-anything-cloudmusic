"""Windows automation backend for NetEase CloudMusic.

This module provides low-level access to control CloudMusic through
Windows API messages and media key simulation.
"""

import subprocess
import os
import time
import sys
from typing import Optional

import psutil
import click

# Virtual Key Codes for Media Keys
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

# INPUT structure for SendInput
INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

# Only import ctypes on Windows systems
if sys.platform == "win32":
    import ctypes

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("ki", KEYBDINPUT),
            ("padding", ctypes.c_ubyte * 8),
        ]

    def _get_user32():
        """Get user32 handle lazily."""
        return ctypes.windll.user32
else:
    # Dummy classes for non-Windows systems to allow import
    class KEYBDINPUT:
        pass

    class INPUT:
        pass

    def _get_user32():
        raise RuntimeError("This functionality requires Windows")


def _send_vk(vk_code: int) -> None:
    """Send a virtual key press using SendInput."""
    extra = ctypes.c_ulong(0)
    user32 = _get_user32()

    # Key down
    ki_down = KEYBDINPUT(vk_code, 0, 0, 0, ctypes.pointer(extra))
    input_down = INPUT(INPUT_KEYBOARD, ki_down)

    # Key up
    ki_up = KEYBDINPUT(vk_code, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    input_up = INPUT(INPUT_KEYBOARD, ki_up)

    inputs = [input_down, input_up]
    n_inputs = len(inputs)
    cb_size = ctypes.sizeof(INPUT)

    user32.SendInput(n_inputs, (INPUT * n_inputs)(*inputs), cb_size)


class CloudMusicBackend:
    """Backend for controlling NetEase CloudMusic via Windows automation."""

    DEFAULT_PATHS = [
        r"D:\Program Files\NetEase\CloudMusic\cloudmusic.exe",
        r"C:\Program Files\NetEase\CloudMusic\cloudmusic.exe",
        r"C:\Program Files (x86)\NetEase\CloudMusic\cloudmusic.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\NetEase\CloudMusic\cloudmusic.exe"),
        r"E:\Program Files\NetEase\CloudMusic\cloudmusic.exe",
        r"F:\Program Files\NetEase\CloudMusic\cloudmusic.exe",
    ]

    # Config file location for custom path (in user's home directory)
    CONFIG_PATH = os.path.expanduser("~/.config/cli-anything-cloudmusic/path.txt")

    def __init__(self, exe_path: Optional[str] = None):
        """Initialize the backend.

        Args:
            exe_path: Path to cloudmusic.exe. If not provided, tries default locations.
        """
        self._exe_path = exe_path or self._find_exe()

    def _find_exe(self) -> Optional[str]:
        """Try to find cloudmusic.exe in various locations.

        Order:
        1. Custom config path from ~/.config/cli-anything-cloudmusic/path.txt
        2. Windows Registry search (uninstall information)
        3. where.exe search
        4. Default paths
        5. Search in Program Files directories
        """
        # 1. Try config file first (user custom path)
        config_path = self._read_config()
        if config_path:
            try:
                if config_path.startswith("/mnt/"):
                    if os.path.exists(config_path):
                        return config_path
                else:
                    if os.path.exists(config_path):
                        return config_path
                    # Try WSL conversion
                    wsl_path = self._windows_to_wsl(config_path)
                    if os.path.exists(wsl_path):
                        return wsl_path
            except Exception:
                pass

        # 2. Try Windows Registry search
        reg_path = self._find_from_registry()
        if reg_path:
            try:
                if os.path.exists(reg_path):
                    return reg_path
                wsl_path = self._windows_to_wsl(reg_path)
                if os.path.exists(wsl_path):
                    return wsl_path
            except Exception:
                pass

        # 3. Try where.exe search
        where_path = self._find_from_where()
        if where_path:
            return where_path

        # 4. Try default paths
        for path in self.DEFAULT_PATHS:
            # Convert WSL paths if needed
            if path.startswith("/mnt/"):
                # Already handled by caller
                continue
            # Check if path exists in Windows
            try:
                if os.path.exists(path):
                    return path
            except OSError:
                continue
            # Try through WSL interop
            try:
                wsl_path = self._windows_to_wsl(path)
                if wsl_path and os.path.exists(wsl_path):
                    return wsl_path
            except Exception:
                continue

        # 5. Search common Program Files directories
        search_drives = ["C", "D", "E", "F"]
        for drive in search_drives:
            for program_dir in [r"\Program Files", r"\Program Files (x86)"]:
                path = fr"{drive}:{program_dir}\NetEase\CloudMusic\cloudmusic.exe"
                try:
                    if os.path.exists(path):
                        return path
                except OSError:
                    pass
                try:
                    wsl_path = self._windows_to_wsl(path)
                    if os.path.exists(wsl_path):
                        return wsl_path
                except Exception:
                    pass

        return None

    def _read_config(self) -> Optional[str]:
        """Read custom path from config file."""
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, 'r') as f:
                    path = f.read().strip()
                    if path:
                        return path
        except Exception:
            return None
        return None

    def _find_from_registry(self) -> Optional[str]:
        """Try to find installation path from Windows Registry via reg query."""
        try:
            # Change to C:\ for CMD compatibility
            original_cwd = os.getcwd()
            try:
                os.chdir("C:")
            except OSError:
                pass

            # Query uninstall registry key
            result = subprocess.run(
                ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "/s", "/f", "CloudMusic"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            try:
                os.chdir(original_cwd)
            except OSError:
                pass

            if result.returncode == 0 and result.stdout:
                lines = result.stdout.splitlines()
                for i, line in enumerate(lines):
                    if "CloudMusic" in line and "DisplayIcon" in line:
                        # DisplayIcon usually has the path to the exe
                        parts = line.split()
                        for part in parts:
                            if part.endswith(".exe"):
                                return part
                    if "CloudMusic" in line and "InstallLocation" in line:
                        parts = line.split()
                        for part in parts[1:]:
                            if part:
                                candidate = os.path.join(part, "cloudmusic.exe")
                                if candidate.endswith("\\cloudmusic.exe"):
                                    return candidate
        except Exception:
            pass
        return None

    def _find_from_where(self) -> Optional[str]:
        """Try where.exe to find cloudmusic.exe."""
        try:
            # Change to C:\ for CMD compatibility
            original_cwd = os.getcwd()
            try:
                os.chdir("C:")
            except OSError:
                pass

            result = subprocess.run(
                ["where", "cloudmusic.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            try:
                os.chdir(original_cwd)
            except OSError:
                pass

            if result.returncode == 0 and result.stdout:
                first_line = result.stdout.splitlines()[0].strip()
                if first_line and os.path.exists(first_line):
                    return first_line
                # Try WSL conversion
                if first_line:
                    wsl_path = self._windows_to_wsl(first_line)
                    if os.path.exists(wsl_path):
                        return wsl_path
        except Exception:
            pass
        return None

    def save_custom_path(self, path: str) -> bool:
        """Save a custom installation path to config file.

        Args:
            path: Path to cloudmusic.exe

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            # Validate path exists before saving
            if os.path.exists(path):
                config_dir = os.path.dirname(self.CONFIG_PATH)
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir, exist_ok=True)
                with open(self.CONFIG_PATH, 'w') as f:
                    f.write(path)
                self._exe_path = path
                return True
            # Try WSL conversion
            if len(path) >= 2 and path[1] == ":":
                wsl_path = self._windows_to_wsl(path)
                if os.path.exists(wsl_path):
                    config_dir = os.path.dirname(self.CONFIG_PATH)
                    if not os.path.exists(config_dir):
                        os.makedirs(config_dir, exist_ok=True)
                    with open(self.CONFIG_PATH, 'w') as f:
                        f.write(wsl_path)
                    self._exe_path = wsl_path
                    return True
            return False
        except Exception:
            return False

    def _windows_to_wsl(self, windows_path: str) -> str:
        """Convert Windows path to WSL path."""
        if len(windows_path) >= 2 and windows_path[1] == ":":
            drive = windows_path[0].lower()
            rest = windows_path[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return windows_path

    def is_running(self) -> bool:
        """Check if CloudMusic is currently running.

        Uses psutil when running on Windows, falls back to tasklist check
        when running from WSL.
        """
        # Try psutil first (works when running on Windows)
        found = False
        try:
            for proc in psutil.process_iter(["name"]):
                try:
                    name = proc.info["name"].lower()
                    if "cloudmusic" in name or "cloudmusic.exe" in name:
                        found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        if found:
            return True

        # Fallback: use Windows tasklist (works when WSL calls Windows Python)
        try:
            # Change to C:\ before running tasklist because CMD doesn't support WSL UNC paths
            original_cwd = os.getcwd()
            try:
                os.chdir("C:")
            except OSError:
                pass
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            try:
                os.chdir(original_cwd)
            except OSError:
                pass
            if result.returncode == 0:
                output = result.stdout.lower()
                if "cloudmusic.exe" in output:
                    return True
        except Exception:
            pass

        return False

    def find_window(self) -> Optional[int]:
        """Find the main window handle of CloudMusic.

        Returns:
            Window handle (HWND) as int, or None if not found.
        """
        # Enumerate all visible windows to find one with "CloudMusic" in title
        # We can't rely on class name alone since it's an Electron app
        try:
            user32 = _get_user32()
            found_hwnd = []

            def enum_callback(hwnd, lParam):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value
                        if title and "CloudMusic" in title:
                            found_hwnd.append(hwnd)
                return 1

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            callback = WNDENUMPROC(enum_callback)
            user32.EnumWindows(callback, None)

            if found_hwnd:
                # Return first visible CloudMusic window
                return int(found_hwnd[0])
            return None
        except Exception:
            return None

    def get_exe_path(self) -> Optional[str]:
        """Get the configured or detected executable path."""
        return self._exe_path

    def launch(self) -> bool:
        """Launch CloudMusic if not already running.

        Returns:
            True if launched successfully, False if already running or failed.
        """
        if self.is_running():
            return False

        if not self._exe_path:
            return False

        try:
            # Check if we're on WSL - if path is /mnt/d/... use cmd start
            if self._exe_path.startswith("/mnt/"):
                # Convert WSL path to Windows path
                windows_path = self._wsl_to_windows(self._exe_path)
                # Change to C:\ before launching because CMD doesn't support WSL UNC paths
                result = subprocess.run(
                    ["cmd.exe", "/c", "start", "", windows_path],
                    cwd="C:\\",
                    capture_output=True
                )
            else:
                # Normal Windows launch
                # For native Windows paths, change to C:\ if cwd is WSL UNC path
                launch_cwd = os.path.dirname(self._exe_path)
                if os.getcwd().startswith('//'):
                    launch_cwd = "C:\\"
                subprocess.Popen(
                    [self._exe_path],
                    cwd=launch_cwd,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            return True
        except Exception as e:
            click.echo(f"Launch error: {e}", err=True)
            return False

    def _wsl_to_windows(self, wsl_path: str) -> str:
        r"""Convert WSL /mnt/c/... path to Windows C:\..."""
        if wsl_path.startswith("/mnt/"):
            parts = wsl_path.split("/")
            drive = parts[2]
            rest = "/".join(parts[3:])
            return f"{drive}:\\{rest}".replace("/", "\\")
        return wsl_path

    def quit(self) -> bool:
        """Quit CloudMusic by terminating the process.

        Returns:
            True if successfully terminated, False if not running.
        """
        if not self.is_running():
            return False

        # Use Windows taskkill to terminate
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "cloudmusic.exe"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return True
        except Exception:
            # Fallback to psutil
            killed = False
            for proc in psutil.process_iter(["name"]):
                try:
                    name = proc.info["name"].lower()
                    if "cloudmusic" in name:
                        proc.terminate()
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return killed

    def send_play_pause(self) -> None:
        """Send play/pause toggle media key."""
        _send_vk(VK_MEDIA_PLAY_PAUSE)

    def send_next_track(self) -> None:
        """Send next track media key."""
        _send_vk(VK_MEDIA_NEXT_TRACK)

    def send_previous_track(self) -> None:
        """Send previous track media key."""
        _send_vk(VK_MEDIA_PREV_TRACK)

    def send_volume_up(self) -> None:
        """Send volume up key."""
        _send_vk(VK_VOLUME_UP)

    def send_volume_down(self) -> None:
        """Send volume down key."""
        _send_vk(VK_VOLUME_DOWN)

    def send_volume_mute(self) -> None:
        """Send mute toggle key."""
        _send_vk(VK_VOLUME_MUTE)

    def send_like_shortcut(self) -> None:
        """Send Ctrl+S shortcut to like/current song.

        This is the default shortcut in NetEase CloudMusic for
        adding the current song to "My Favorites".
        """
        # Send Ctrl+S using SendInput with modifier
        extra = ctypes.c_ulong(0)
        user32 = _get_user32()

        # VK_CONTROL = 0x11, VK_S = 0x53
        VK_CONTROL = 0x11
        VK_S = 0x53

        # Press Ctrl
        ki_ctrl_down = KEYBDINPUT(VK_CONTROL, 0, 0, 0, ctypes.pointer(extra))
        input_ctrl_down = INPUT(INPUT_KEYBOARD, ki_ctrl_down)

        # Press S
        ki_s_down = KEYBDINPUT(VK_S, 0, 0, 0, ctypes.pointer(extra))
        input_s_down = INPUT(INPUT_KEYBOARD, ki_s_down)

        # Release S
        ki_s_up = KEYBDINPUT(VK_S, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        input_s_up = INPUT(INPUT_KEYBOARD, ki_s_up)

        # Release Ctrl
        ki_ctrl_up = KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        input_ctrl_up = INPUT(INPUT_KEYBOARD, ki_ctrl_up)

        inputs = [input_ctrl_down, input_s_down, input_s_up, input_ctrl_up]
        n_inputs = len(inputs)
        cb_size = ctypes.sizeof(INPUT)

        user32.SendInput(n_inputs, (INPUT * n_inputs)(*inputs), cb_size)

        # Small delay to ensure the keys are processed
        time.sleep(0.05)

    def get_window_title(self) -> Optional[str]:
        """Get the current window title of the main window.

        Note: This uses a simple enumeration approach that works for WSL.
        """
        # On Windows, we could use GetWindowText directly
        # From WSL, we rely on the fact that when running through Windows Python
        # ctypes can access user32
        try:
            user32 = _get_user32()
            # We need to enumerate all windows to find the one with CloudMusic
            titles = []

            def enum_callback(hwnd, lParam):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value
                        if title and "CloudMusic" in title:
                            titles.append(title)
                return 1

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            callback = WNDENUMPROC(enum_callback)
            user32.EnumWindows(callback, None)

            if titles:
                # Return first title containing CloudMusic
                return titles[0]
            return None
        except Exception:
            return None

    def bring_to_front(self) -> bool:
        """Bring the CloudMusic window to the foreground.

        Returns:
            True if successful, False if window not found.
        """
        # Simple implementation - more could be done with SetForegroundWindow
        # For basic usage, just ensure it's not minimized
        try:
            user32 = _get_user32()
            hwnd = self.find_window()
            if hwnd:
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                return True
        except Exception:
            pass
        return False

    def minimize(self) -> bool:
        """Minimize the CloudMusic window.

        Returns:
            True if successful, False if window not found.
        """
        try:
            user32 = _get_user32()
            hwnd = self.find_window()
            if hwnd:
                user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
                return True
        except Exception:
            pass
        return False
