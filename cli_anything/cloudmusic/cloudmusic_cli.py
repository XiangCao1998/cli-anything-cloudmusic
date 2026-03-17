"""Main CLI entry point for NetEase CloudMusic CLI."""

import json
import os
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

from .utils import CloudMusicBackend, WindowDetector
from .core.playback import PlaybackController
from .core.volume import VolumeController
from .core.track import TrackInfoRetriever


def print_result(result, json_output: bool):
    """Print result either as human-readable or JSON."""
    if json_output:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if isinstance(result, dict):
            for key, value in result.items():
                if value is not None and value != "":
                    click.secho(f"{key}: ", nl=False, bold=True)
                    click.echo(f"{value}")
        else:
            click.echo(result)


@click.group(invoke_without_command=True)
@click.option("--json", "json_output", is_flag=True, default=False, help="Output JSON format for machine consumption.")
@click.pass_context
def main(ctx, json_output):
    """CLI interface for NetEase CloudMusic (网易云音乐).

    Control playback, adjust volume, and get current track info from the command line.
    """
    # Initialize backend and controllers
    ctx.obj = {
        "backend": CloudMusicBackend(),
        "json_output": json_output,
    }
    backend = ctx.obj["backend"]
    ctx.obj["detector"] = WindowDetector(backend)
    ctx.obj["playback"] = PlaybackController(backend)
    ctx.obj["volume"] = VolumeController(backend)
    ctx.obj["track"] = TrackInfoRetriever(backend, ctx.obj["detector"])

    # If no command given, start REPL
    if ctx.invoked_subcommand is None:
        repl()


@main.command(name="launch")
@click.pass_context
def launch(ctx):
    """Launch NetEase CloudMusic if not already running."""
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    if backend.is_running():
        print_result({"success": True, "message": "CloudMusic is already running"}, json_output)
        return

    success = backend.launch()
    if success:
        print_result({"success": True, "message": "CloudMusic launched successfully"}, json_output)
    else:
        if not backend.get_exe_path():
            print_result({
                "success": False,
                "error": (
                    "Could not find CloudMusic installation automatically. "
                    "Please set custom path with:\n"
                    "  cli-anything-cloudmusic config <path-to-cloudmusic.exe>"
                )
            }, json_output)
        else:
            print_result({"success": False, "error": "Failed to launch CloudMusic"}, json_output)


@main.command(name="quit")
@click.pass_context
def quit(ctx):
    """Quit NetEase CloudMusic."""
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    if not backend.is_running():
        print_result({"success": True, "message": "CloudMusic is not running"}, json_output)
        return

    success = backend.quit()
    if success:
        print_result({"success": True, "message": "CloudMusic quit successfully"}, json_output)
    else:
        print_result({"success": False, "error": "Failed to quit CloudMusic"}, json_output)


@main.command(name="show")
@click.pass_context
def show(ctx):
    """Bring CloudMusic window to foreground."""
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    if not backend.is_running():
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
        return

    success = backend.bring_to_front()
    print_result({"success": success}, json_output)


@main.command(name="hide")
@click.pass_context
def hide(ctx):
    """Minimize CloudMusic window to tray."""
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    if not backend.is_running():
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
        return

    success = backend.minimize()
    print_result({"success": success}, json_output)


@main.command(name="play")
@click.pass_context
def play(ctx):
    """Start or resume playback."""
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.play()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True, "message": "Playback started"}, json_output)


@main.command(name="pause")
@click.pass_context
def pause(ctx):
    """Pause current playback."""
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.pause()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True, "message": "Playback paused"}, json_output)


@main.command(name="toggle")
@click.pass_context
def toggle(ctx):
    """Toggle play/pause state."""
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.toggle()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True}, json_output)


@main.command(name="next")
@click.pass_context
def next_track(ctx):
    """Skip to next track."""
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.next()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True}, json_output)


@main.command(name="previous")
@click.pass_context
def previous_track(ctx):
    """Go to previous track."""
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.previous()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True}, json_output)


@main.command(name="like")
@click.pass_context
def like(ctx):
    """Like/favorite the current track (toggles favorite state).

    Uses the default NetEase CloudMusic shortcut Ctrl+S.
    """
    playback = ctx.obj["playback"]
    json_output = ctx.obj["json_output"]

    success = playback.like()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True, "message": "Like shortcut sent (toggled favorite state)"}, json_output)


@main.command(name="volume")
@click.argument("action", required=False, type=click.Choice(["set", "up", "down"]))
@click.argument("value", required=False, type=int)
@click.pass_context
def volume(ctx, action, value):
    """Get or set volume.

    \b
    Usage:
      volume             - Show current volume
      volume set <0-100> - Set volume to specific level
      volume up [delta]  - Increase volume (default: 10)
      volume down [delta]- Decrease volume (default: 10)
    """
    volume_ctrl = ctx.obj["volume"]
    json_output = ctx.obj["json_output"]

    if not volume_ctrl.is_running():
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
        return

    if action is None:
        # Currently we can't get exact volume level via this approach
        print_result({"message": "Volume control available via up/down/toggle"}, json_output)
        return

    delta = value if value is not None else 10

    if action == "up":
        success = volume_ctrl.up(delta)
        print_result({"success": success, "message": f"Increased volume by {delta}"}, json_output)
    elif action == "down":
        success = volume_ctrl.down(delta)
        print_result({"success": success, "message": f"Decreased volume by {delta}"}, json_output)
    elif action == "set":
        if value is None:
            print_result({"success": False, "error": "Please provide volume percentage 0-100"}, json_output)
        else:
            success = volume_ctrl.set(value)
            print_result({"success": success, "message": f"Volume set to {value}%"}, json_output)


@main.command(name="mute")
@click.pass_context
def mute(ctx):
    """Toggle mute state."""
    volume_ctrl = ctx.obj["volume"]
    json_output = ctx.obj["json_output"]

    success = volume_ctrl.toggle_mute()
    if not success:
        print_result({"success": False, "error": "CloudMusic is not running"}, json_output)
    else:
        print_result({"success": True, "message": "Mute toggled"}, json_output)


@main.command(name="current")
@click.pass_context
def current(ctx):
    """Show current playing track information."""
    track_info = ctx.obj["track"]
    json_output = ctx.obj["json_output"]

    current = track_info.get_current()
    result = {
        "success": current.running,
        "title": current.title,
        "artist": current.artist,
        "running": current.running,
    }
    print_result(result, json_output)


@main.command(name="status")
@click.pass_context
def status(ctx):
    """Show current playback status."""
    track_info = ctx.obj["track"]
    json_output = ctx.obj["json_output"]

    status = track_info.get_status()
    status["success"] = status["running"]
    print_result(status, json_output)


@main.command(name="config")
@click.argument("path", required=True)
@click.pass_context
def config(ctx, path):
    """Configure custom path to cloudmusic.exe.

    Saves the path to config file for persistent use.

    Example:
      cli-anything-cloudmusic config "C:\\Program Files\\NetEase\\CloudMusic\\cloudmusic.exe"
      cli-anything-cloudmusic config "/mnt/d/Program Files/NetEase/CloudMusic/cloudmusic.exe"
    """
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    # Check if path exists
    if not os.path.exists(path):
        # Try WSL path conversion if needed
        # Maybe the user gave Windows path but we're on WSL
        try:
            wsl_path = backend._windows_to_wsl(path)
            if os.path.exists(wsl_path):
                path = wsl_path
        except Exception:
            pass

    success = backend.save_custom_path(path)
    if success:
        print_result({
            "success": True,
            "message": f"Custom path saved: {path}",
            "path": path
        }, json_output)
    else:
        print_result({
            "success": False,
            "error": "Failed to save custom path"
        }, json_output)


@main.command(name="detect")
@click.pass_context
def detect(ctx):
    """Detect cloudmusic installation automatically."""
    backend = ctx.obj["backend"]
    json_output = ctx.obj["json_output"]

    found_path = backend.get_exe_path()
    if found_path:
        print_result({
            "success": True,
            "message": f"CloudMusic found at: {found_path}",
            "path": found_path
        }, json_output)
    else:
        print_result({
            "success": False,
            "error": (
                "Could not automatically find CloudMusic installation. "
                "Use `cli-anything-cloudmusic config <path>` to set custom path."
            )
        }, json_output)


def repl():
    """Start interactive REPL mode."""
    commands = [
        "launch", "quit", "show", "hide",
        "play", "pause", "toggle", "next", "previous", "like",
        "volume", "mute", "current", "status",
        "config", "detect",
        "exit", "help",
    ]

    completer = WordCompleter(commands)
    style = Style.from_dict({
        "prompt": "#ansiblue bold",
    })

    session = PromptSession(
        "cloudmusic> ",
        completer=completer,
        style=style,
    )

    click.secho("=== 网易云音乐 CLI - Interactive REPL ===", bold=True)
    click.echo("Type help or ? to see commands. Type exit to quit.")
    click.echo()

    while True:
        try:
            text = session.prompt()
            text = text.strip()
            if not text:
                continue
            if text.lower() in ("exit", "quit", "q"):
                break
            if text.lower() in ("help", "?"):
                click.echo("Available commands:")
                for cmd in sorted(commands):
                    click.echo(f"  {cmd}")
                click.echo()
                continue

            # Parse and execute command
            args = text.split()
            main(args, standalone_mode=False)
            click.echo()

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            click.echo()


if __name__ == "__main__":
    main()
