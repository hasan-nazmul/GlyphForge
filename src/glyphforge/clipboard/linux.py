"""Linux clipboard provider.

Detects and uses available clipboard tools: wl-paste/wl-copy, xclip, xsel.
Provides clear error messages when no clipboard provider is found.
"""

from __future__ import annotations

import shutil
import subprocess


class ClipboardError(Exception):
    """Raised when clipboard operations fail."""

    pass


def read_clipboard() -> str:
    """Read text content from the system clipboard.

    Tries providers in order: wl-paste (Wayland), xclip, xsel (X11).

    Raises
    ------
    ClipboardError
        If no supported clipboard provider is found or the read fails.
    """
    providers = [
        ("wl-paste", ["wl-paste", "--no-newline"]),
        ("xclip", ["xclip", "-selection", "clipboard", "-o"]),
        ("xsel", ["xsel", "--clipboard", "--output"]),
    ]

    for name, cmd in providers:
        if shutil.which(cmd[0]) is not None:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return result.stdout
                # Provider found but failed — try next
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue

    raise ClipboardError(
        "No supported clipboard provider found.\n\n"
        "Install one of the following:\n"
        "  Wayland:  sudo apt install wl-clipboard\n"
        "  X11:      sudo apt install xclip\n"
        "  X11:      sudo apt install xsel"
    )


def write_clipboard(text: str) -> None:
    """Write text content to the system clipboard.

    Tries providers in order: wl-copy (Wayland), xclip, xsel (X11).

    Raises
    ------
    ClipboardError
        If no supported clipboard provider is found or the write fails.
    """
    providers = [
        ("wl-copy", ["wl-copy"]),
        ("xclip", ["xclip", "-selection", "clipboard"]),
        ("xsel", ["xsel", "--clipboard", "--input"]),
    ]

    for name, cmd in providers:
        if shutil.which(cmd[0]) is not None:
            try:
                result = subprocess.run(
                    cmd,
                    input=text,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue

    raise ClipboardError(
        "No supported clipboard provider found to write to clipboard.\n\n"
        "Install one of the following:\n"
        "  Wayland:  sudo apt install wl-clipboard\n"
        "  X11:      sudo apt install xclip\n"
        "  X11:      sudo apt install xsel"
    )
