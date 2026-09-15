"""Tests for the normalizer (Pass 1 sentinel replacement)."""

from glyphforge.parser.normalizer import SENTINEL_PREFIX, normalize


class TestCodeBlockProtection:
    """Test that fenced code blocks are replaced with sentinels."""

    def test_code_block_replaced(self):
        text = '```python\nprint("hello")\n```'
        result = normalize(text)
        assert "```" not in result.text
        assert SENTINEL_PREFIX in result.text
        # Verify sentinel map has the code
        entries = [e for e in result.sentinel_map.values() if e.kind == "code_block"]
        assert len(entries) == 1
        assert entries[0].content == 'print("hello")'
        assert entries[0].language == "python"

    def test_multiple_code_blocks(self):
        text = "```python\na()\n```\n\nText\n\n```js\nb()\n```"
        result = normalize(text)
        entries = [e for e in result.sentinel_map.values() if e.kind == "code_block"]
        assert len(entries) == 2


class TestDisplayMathProtection:
    """Test that display math blocks are replaced with sentinels."""

    def test_dollar_display_math(self):
        text = "Before\n$$\nE = mc^2\n$$\nAfter"
        result = normalize(text)
        assert "$$" not in result.text
        entries = [e for e in result.sentinel_map.values() if e.kind == "display_math"]
        assert len(entries) == 1
        assert "E = mc^2" in entries[0].content

    def test_bracket_display_math(self):
        text = "Before\n\\[\nx^2 + y^2\n\\]\nAfter"
        result = normalize(text)
        assert "\\[" not in result.text
        entries = [e for e in result.sentinel_map.values() if e.kind == "display_math"]
        assert len(entries) == 1


class TestInlineMathProtection:
    """Test that inline math is replaced with sentinels."""

    def test_inline_dollar_math(self):
        text = "The value $x^2$ is important."
        result = normalize(text)
        entries = [e for e in result.sentinel_map.values() if e.kind == "inline_math"]
        assert len(entries) == 1
        assert entries[0].content == "x^2"

    def test_currency_not_replaced(self):
        text = "This costs $100 and $5.99 each."
        result = normalize(text)
        entries = [e for e in result.sentinel_map.values() if e.kind == "inline_math"]
        assert len(entries) == 0
        # Currency should remain in text
        assert "$100" in result.text or "100" in result.text


class TestMixedContent:
    """Test normalization with mixed code, math, and text."""

    def test_code_and_math(self):
        text = "```python\nx = $y\n```\n\nThe value $z^2$ matters."
        result = normalize(text)
        code_entries = [e for e in result.sentinel_map.values() if e.kind == "code_block"]
        math_entries = [e for e in result.sentinel_map.values() if e.kind == "inline_math"]
        assert len(code_entries) == 1
        assert len(math_entries) == 1
        # The $ inside code should NOT be treated as math
        assert code_entries[0].content == "x = $y"
