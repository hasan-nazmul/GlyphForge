"""Tests for the math lexer state machine."""

import pytest

from glyphforge.parser.math_lexer import MathKind, MathSpan, scan_math


class TestInlineMath:
    """Test inline math detection with $...$ and \\(...\\)."""

    def test_simple_dollar(self):
        spans = scan_math("The value $x^2$ is important.")
        assert len(spans) == 1
        assert spans[0].kind == MathKind.INLINE
        assert spans[0].latex == "x^2"

    def test_multiple_inline(self):
        spans = scan_math("Given $x$ and $y$, compute $z$.")
        assert len(spans) == 3
        assert all(s.kind == MathKind.INLINE for s in spans)
        assert spans[0].latex == "x"
        assert spans[1].latex == "y"
        assert spans[2].latex == "z"

    def test_backslash_paren(self):
        spans = scan_math(r"The value \(x^2 + y^2\) is important.")
        assert len(spans) == 1
        assert spans[0].kind == MathKind.INLINE
        assert spans[0].latex == "x^2 + y^2"

    def test_inline_with_frac(self):
        spans = scan_math(r"Result: $\frac{a}{b}$")
        assert len(spans) == 1
        assert spans[0].latex == r"\frac{a}{b}"

    def test_inline_greek(self):
        spans = scan_math(r"The angle $\alpha$ is small.")
        assert len(spans) == 1
        assert spans[0].latex == r"\alpha"


class TestDisplayMath:
    """Test display math detection with $$...$$ and \\[...\\]."""

    def test_dollar_display(self):
        spans = scan_math("Before\n$$E = mc^2$$\nAfter")
        assert len(spans) == 1
        assert spans[0].kind == MathKind.DISPLAY
        assert "E = mc^2" in spans[0].latex

    def test_bracket_display(self):
        text = r"Before\[x^2 + y^2\]After"
        spans = scan_math(text)
        assert len(spans) == 1
        assert spans[0].kind == MathKind.DISPLAY

    def test_multiline_dollar_display(self):
        text = "Before\n$$\nJ(\\theta)\n=\n\\frac{1}{m}\n$$\nAfter"
        spans = scan_math(text)
        assert len(spans) == 1
        assert spans[0].kind == MathKind.DISPLAY
        assert "J(\\theta)" in spans[0].latex


class TestCurrencyDetection:
    """Test that currency amounts are NOT detected as math."""

    def test_integer_currency(self):
        spans = scan_math("This costs $100.")
        assert len(spans) == 0

    def test_decimal_currency(self):
        spans = scan_math("The price is $5.99 per unit.")
        assert len(spans) == 0

    def test_currency_and_math_mixed(self):
        spans = scan_math("The price is $100 and the variable $x$ matters.")
        assert len(spans) == 1
        assert spans[0].latex == "x"

    def test_large_currency(self):
        spans = scan_math("Revenue was $1,000,000 this quarter.")
        assert len(spans) == 0


class TestShellVariables:
    """Test that shell variables are NOT detected as math."""

    def test_path_variable(self):
        spans = scan_math("Set $PATH to include /usr/local/bin.")
        assert len(spans) == 0

    def test_home_variable(self):
        spans = scan_math("The home directory is $HOME.")
        assert len(spans) == 0


class TestCodeSpanProtection:
    """Test that dollar signs inside code spans are ignored."""

    def test_dollar_in_code(self):
        spans = scan_math("Use `$variable` in your script.")
        assert len(spans) == 0

    def test_dollar_in_double_backtick(self):
        spans = scan_math("Use `` $x^2 `` in LaTeX.")
        assert len(spans) == 0


class TestEscapedDollar:
    """Test that escaped dollar signs are ignored."""

    def test_escaped_dollar(self):
        spans = scan_math(r"The cost is \$100.")
        assert len(spans) == 0


class TestEdgeCases:
    """Edge cases and tricky inputs."""

    def test_empty_string(self):
        spans = scan_math("")
        assert len(spans) == 0

    def test_no_math(self):
        spans = scan_math("Just plain text with no math at all.")
        assert len(spans) == 0

    def test_dollar_at_end(self):
        spans = scan_math("text $")
        assert len(spans) == 0

    def test_empty_dollar(self):
        # $ $ should not be math (space after opening $)
        spans = scan_math("text $ $ more")
        assert len(spans) == 0
