"""Tests for the deterministic cleaner."""

from glyphforge.cleaners.deterministic import DeterministicCleaner


class TestDeterministicCleaner:
    def setup_method(self):
        self.cleaner = DeterministicCleaner()

    def test_normalize_line_endings(self):
        text = "hello\r\nworld\rend"
        result = self.cleaner.clean(text)
        assert "\r" not in result

    def test_trailing_whitespace(self):
        text = "hello   \nworld\t\t\n"
        result = self.cleaner.clean(text)
        for line in result.split("\n"):
            if line:  # Skip empty lines
                assert not line.endswith(" ") or line.endswith("  ")  # hard break OK
                assert not line.endswith("\t")

    def test_excessive_blank_lines(self):
        text = "hello\n\n\n\n\nworld\n"
        result = self.cleaner.clean(text)
        assert "\n\n\n" not in result  # Max 2 consecutive newlines

    def test_heading_spacing(self):
        text = "Some text\n## Heading"
        result = self.cleaner.clean(text)
        # Should have blank line before heading
        assert "\n\n## Heading" in result

    def test_tilde_to_backtick(self):
        text = "~~~python\ncode\n~~~\n"
        result = self.cleaner.clean(text)
        assert "```python" in result
        assert "~~~" not in result

    def test_list_marker_normalization(self):
        text = "* Item 1\n+ Item 2\n- Item 3\n"
        result = self.cleaner.clean(text)
        assert result.count("- ") == 3

    def test_trailing_newline(self):
        result = self.cleaner.clean("hello")
        assert result.endswith("\n")
        assert not result.endswith("\n\n")

    def test_idempotent(self):
        text = "# Hello\n\n- Item\n\n```python\ncode\n```\n"
        first = self.cleaner.clean(text)
        second = self.cleaner.clean(first)
        assert first == second
