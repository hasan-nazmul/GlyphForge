"""Tests for Linux clipboard reading and writing with mocked providers."""

from unittest.mock import MagicMock, patch

import pytest

from glyphforge.clipboard.linux import ClipboardError, read_clipboard, write_clipboard


class TestClipboardRead:
    def test_read_wayland_wl_paste(self):
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.side_effect = lambda cmd: "/usr/bin/wl-paste" if cmd == "wl-paste" else None
            mock_run.return_value = MagicMock(returncode=0, stdout="clipboard content from wl-paste")

            content = read_clipboard()
            assert content == "clipboard content from wl-paste"
            mock_run.assert_called_once_with(
                ["wl-paste", "--no-newline"],
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_read_xclip_fallback(self):
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.side_effect = lambda cmd: "/usr/bin/xclip" if cmd == "xclip" else None
            mock_run.return_value = MagicMock(returncode=0, stdout="clipboard content from xclip")

            content = read_clipboard()
            assert content == "clipboard content from xclip"
            mock_run.assert_called_once_with(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_read_xsel_fallback(self):
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.side_effect = lambda cmd: "/usr/bin/xsel" if cmd == "xsel" else None
            mock_run.return_value = MagicMock(returncode=0, stdout="clipboard content from xsel")

            content = read_clipboard()
            assert content == "clipboard content from xsel"

    def test_read_no_provider_raises_clipboard_error(self):
        with patch("shutil.which", return_value=None):
            with pytest.raises(ClipboardError) as exc_info:
                read_clipboard()
            assert "No supported clipboard provider found" in str(exc_info.value)
            assert "sudo apt install" in str(exc_info.value)


class TestClipboardWrite:
    def test_write_wayland_wl_copy(self):
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.side_effect = lambda cmd: "/usr/bin/wl-copy" if cmd == "wl-copy" else None
            mock_run.return_value = MagicMock(returncode=0)

            write_clipboard("test text")
            mock_run.assert_called_once_with(
                ["wl-copy"],
                input="test text",
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_write_xclip_fallback(self):
        with patch("shutil.which") as mock_which, patch("subprocess.run") as mock_run:
            mock_which.side_effect = lambda cmd: "/usr/bin/xclip" if cmd == "xclip" else None
            mock_run.return_value = MagicMock(returncode=0)

            write_clipboard("test text")
            mock_run.assert_called_once_with(
                ["xclip", "-selection", "clipboard"],
                input="test text",
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_write_no_provider_raises_clipboard_error(self):
        with patch("shutil.which", return_value=None):
            with pytest.raises(ClipboardError) as exc_info:
                write_clipboard("some text")
            assert "No supported clipboard provider found" in str(exc_info.value)
