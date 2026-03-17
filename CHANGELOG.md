# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-18

### Added
- Initial release
- Playback control: play, pause, toggle, next, previous, like
- Volume control: up, down, set, mute toggle
- Track info: current title/artist retrieval
- App control: launch, quit, show, hide window
- Auto-discovery of CloudMusic installation
- Configurable custom path
- REPL interactive mode
- JSON output for AI agent consumption
- WSL support (Windows Python from WSL terminal)

### Infrastructure
- Modern Python packaging with pyproject.toml (PEP 626)
- GitHub Actions CI with Windows testing (Python 3.8-3.12)
- Ruff for linting and formatting
- Mypy for type checking
- pre-commit hooks
- Issue and PR templates
- Dependabot for dependency updates
- Automatic PyPI publishing on release
