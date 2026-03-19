# Contributing

Thank you for your interest in contributing to `cli-anything-cloudmusic`!

## Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/your-username/cli-anything-cloudmusic.git
cd cli-anything-cloudmusic
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**
```bash
pip install -e .
pip install ruff mypy pytest pytest-cov pre-commit
```

4. **Install pre-commit hooks**
```bash
pre-commit install
```

## Running Checks

Before submitting a pull request, make sure all checks pass:

### Lint and Format
```bash
ruff check .          # Run linter
ruff check --fix .    # Fix auto-fixable issues
ruff format .         # Format code
```

### Type Check
```bash
mypy .
```

### Run Tests
```bash
pytest -v
```

With coverage:
```bash
pytest --cov=cli_anything.cloudmusic --cov-report=term --cov-report=html
```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all checks pass
4. Push your branch and open a Pull Request
5. Wait for CI to pass and review

## Code Style

This project uses:
- **ruff** for linting and formatting (fast all-in-one tool)
- **mypy** for static type checking
- **pre-commit** to run checks automatically before commits

We follow PEP 8 guidelines with a line length of 88 characters.

## Testing

- All new features should include tests
- Bug fixes should include tests that verify the fix
- Keep test coverage above 80% when possible

Tests are located in `cli_anything/cloudmusic/tests/`

## Windows Specific

This is a Windows-specific package that relies on `pywin32` for Windows API access.
- All functionality requires Windows to run
- CI runs full tests only on Windows
- Linting and type checking run on Ubuntu CI
- WSL is supported but requires Windows Python

## Pull Request Process

1. Update the README.md with details of any new features
2. Update the CHANGELOG/DEVELOPMENT_LOG if applicable
3. All CI checks must pass before merging can occur
4. The PR can be merged once you get approval from a maintainer
5. Follow the conventional commit format for your PR title

## CI Checks and Branch Protection

This project enforces strict quality checks through GitHub CI:

- **pre-commit**: Runs all pre-commit hooks (ruff lint, ruff format, mypy, trailing whitespace check, yaml check)
- **lint**: Runs standalone lint, format check, and type checking
- **test**: Runs full test matrix across Python 3.8-3.12 on both Ubuntu and Windows
- **security**: Checks for critical dependency vulnerabilities with `pip-audit`

Branch protection is enabled on the `main` branch:
- **All CI checks must pass** before any pull request can be merged
- **Branch must be up to date** with main before merging
- At least one approval from a Code Owner is required

This ensures that `main` always remains in a working, secure state.

## Release Process

- Maintainers tag releases with `v*` (e.g. `v0.1.0`)
- GitHub Actions automatically publishes to PyPI when a release is created

## Code of Conduct

Be respectful and inclusive of others. We expect all contributors to adhere to professional standards of behavior.
