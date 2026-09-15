"""External dependency detection and guidance.

Checks for required system binaries (pandoc, tectonic, xelatex, clipboard tools)
and provides actionable installation instructions when dependencies are missing.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass


@dataclass
class DependencyStatus:
    """Status of a single external dependency."""

    name: str
    found: bool
    path: str | None = None
    version: str | None = None
    install_hint: str = ""


def check_pandoc() -> DependencyStatus:
    """Check whether Pandoc is available."""
    path = shutil.which("pandoc")
    if path:
        version = _get_version(path, "--version")
        return DependencyStatus(name="pandoc", found=True, path=path, version=version)
    return DependencyStatus(
        name="pandoc",
        found=False,
        install_hint=(
            "Install Pandoc:\n"
            "  Ubuntu/Debian:  sudo apt update && sudo apt install -y pandoc\n"
            "  Or download:    https://github.com/jgm/pandoc/releases"
        ),
    )


def check_tectonic() -> DependencyStatus:
    """Check whether Tectonic (TeX engine) is available."""
    path = shutil.which("tectonic")
    if path:
        version = _get_version(path, "--version")
        return DependencyStatus(name="tectonic", found=True, path=path, version=version)
    return DependencyStatus(
        name="tectonic",
        found=False,
        install_hint=(
            "Install Tectonic:\n"
            "  curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh\n"
            "  Or with cargo:  cargo install tectonic\n"
            "  Or use XeLaTeX: sudo apt install -y texlive-xetex"
        ),
    )


def check_xelatex() -> DependencyStatus:
    """Check whether XeLaTeX is available."""
    path = shutil.which("xelatex")
    if path:
        version = _get_version(path, "--version")
        return DependencyStatus(name="xelatex", found=True, path=path, version=version)
    return DependencyStatus(
        name="xelatex",
        found=False,
        install_hint=(
            "Install XeLaTeX:\n"
            "  Ubuntu/Debian:  sudo apt install -y texlive-xetex texlive-fonts-recommended"
        ),
    )


def check_clipboard_tools() -> DependencyStatus:
    """Check whether any supported Linux clipboard utility is available."""
    for tool in ("wl-paste", "xclip", "xsel"):
        path = shutil.which(tool)
        if path:
            return DependencyStatus(name=tool, found=True, path=path)
    return DependencyStatus(
        name="clipboard",
        found=False,
        install_hint=(
            "Install clipboard tools:\n"
            "  Wayland:  sudo apt install -y wl-clipboard\n"
            "  X11:      sudo apt install -y xclip"
        ),
    )


def check_all() -> list[DependencyStatus]:
    """Check all known external dependencies."""
    return [check_pandoc(), check_tectonic(), check_xelatex(), check_clipboard_tools()]


def _get_version(path: str, flag: str) -> str | None:
    """Run *path* with *flag* and extract the first line of output."""
    import subprocess

    try:
        result = subprocess.run(
            [path, flag],
            capture_output=True,
            text=True,
            timeout=10,
        )
        first_line = result.stdout.strip().split("\n")[0]
        return first_line
    except Exception:
        return None
