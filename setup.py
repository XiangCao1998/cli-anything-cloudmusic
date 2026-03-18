"""Backward compatibility shim for legacy installation methods.

Modern installation should use pyproject.toml with pip.
This file is kept for backward compatibility only.
"""

from setuptools import setup

# All configuration is now in pyproject.toml
setup()
