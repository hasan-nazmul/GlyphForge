"""Round-trip tests: parse → render → parse → render should be idempotent.

The invariant: normalize(normalize(input)) == normalize(input)
"""

from pathlib import Path

import pytest

from glyphforge.parser.markdown_parser import parse
from glyphforge.renderers.markdown import render_markdown


def _roundtrip(text: str) -> tuple[str, str]:
    """Parse text, render to canonical MD, then parse and render again."""
    doc1 = parse(text)
    md1 = render_markdown(doc1)
    doc2 = parse(md1)
    md2 = render_markdown(doc2)
    return md1, md2


class TestRoundTrip:
    def test_basic_roundtrip(self, basic_md):
        md1, md2 = _roundtrip(basic_md)
        assert md1 == md2, "Basic Markdown not idempotent after round-trip"

    def test_code_roundtrip(self, code_md):
        md1, md2 = _roundtrip(code_md)
        assert md1 == md2, "Code blocks not idempotent after round-trip"

    def test_table_roundtrip(self, tables_md):
        md1, md2 = _roundtrip(tables_md)
        assert md1 == md2, "Tables not idempotent after round-trip"

    def test_math_roundtrip(self, math_md):
        md1, md2 = _roundtrip(math_md)
        assert md1 == md2, "Math not idempotent after round-trip"

    def test_demo_roundtrip(self, demo_md):
        md1, md2 = _roundtrip(demo_md)
        assert md1 == md2, "Demo document not idempotent after round-trip"

    def test_simple_paragraph(self):
        md1, md2 = _roundtrip("Hello world.\n")
        assert md1 == md2

    def test_heading_and_paragraph(self):
        md1, md2 = _roundtrip("# Title\n\nSome text.\n")
        assert md1 == md2

    def test_display_math(self):
        md1, md2 = _roundtrip("$$\nE = mc^2\n$$\n")
        assert md1 == md2

    def test_inline_math(self):
        md1, md2 = _roundtrip("The value $x^2$ is important.\n")
        assert md1 == md2
