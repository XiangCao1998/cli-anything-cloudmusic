from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-cloudmusic",
    version="0.1.0",
    author="CLI-Anything",
    description="CLI interface for NetEase CloudMusic (网易云音乐)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={
        "cli_anything.cloudmusic": ["skills/SKILL.md"],
    },
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "pywin32>=300",
        "psutil>=5.8",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-cloudmusic = cli_anything.cloudmusic.cloudmusic_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    keywords="cli cli-anything netease cloudmusic music player",
)
