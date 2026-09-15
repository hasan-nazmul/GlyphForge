"""Tests for the canonical Markdown renderer."""

from glyphforge.model.blocks import (
    CodeBlock,
    DisplayMath,
    Heading,
    List,
    ListItem,
    Paragraph,
    Table,
    TableAlignment,
    TableCell,
    ThematicBreak,
    BlockQuote,
)
from glyphforge.model.document import Document, Metadata
from glyphforge.model.inlines import Bold, InlineCode, InlineMath, Italic, Text
from glyphforge.renderers.markdown import render_markdown


class TestHeadingRendering:
    def test_h1(self):
        doc = Document(blocks=[Heading(level=1, children=[Text("Hello")])])
        result = render_markdown(doc)
        assert "# Hello" in result

    def test_h3(self):
        doc = Document(blocks=[Heading(level=3, children=[Text("Sub")])])
        result = render_markdown(doc)
        assert "### Sub" in result


class TestParagraphRendering:
    def test_plain_text(self):
        doc = Document(blocks=[Paragraph(children=[Text("Hello world.")])])
        result = render_markdown(doc)
        assert "Hello world." in result

    def test_bold(self):
        doc = Document(blocks=[Paragraph(children=[Bold(children=[Text("bold")])])])
        result = render_markdown(doc)
        assert "**bold**" in result

    def test_italic(self):
        doc = Document(blocks=[Paragraph(children=[Italic(children=[Text("em")])])])
        result = render_markdown(doc)
        assert "*em*" in result

    def test_inline_code(self):
        doc = Document(blocks=[Paragraph(children=[InlineCode(code="x")])])
        result = render_markdown(doc)
        assert "`x`" in result

    def test_inline_math(self):
        doc = Document(blocks=[Paragraph(children=[InlineMath(latex="x^2")])])
        result = render_markdown(doc)
        assert "$x^2$" in result


class TestCodeBlockRendering:
    def test_with_language(self):
        doc = Document(blocks=[CodeBlock(code='print("hi")', language="python")])
        result = render_markdown(doc)
        assert "```python" in result
        assert 'print("hi")' in result
        assert result.count("```") == 2

    def test_without_language(self):
        doc = Document(blocks=[CodeBlock(code="raw code")])
        result = render_markdown(doc)
        assert "```\n" in result


class TestDisplayMathRendering:
    def test_simple(self):
        doc = Document(blocks=[DisplayMath(latex="E = mc^2")])
        result = render_markdown(doc)
        assert "$$\nE = mc^2\n$$" in result

    def test_multiline(self):
        doc = Document(blocks=[DisplayMath(latex="J(\\theta)\n=\n\\frac{1}{m}")])
        result = render_markdown(doc)
        assert "$$" in result
        assert "J(\\theta)" in result


class TestTableRendering:
    def test_basic_table(self):
        doc = Document(
            blocks=[
                Table(
                    headers=[TableCell(children=[Text("A")]), TableCell(children=[Text("B")])],
                    rows=[[TableCell(children=[Text("1")]), TableCell(children=[Text("2")])]],
                    alignments=[TableAlignment.NONE, TableAlignment.NONE],
                )
            ]
        )
        result = render_markdown(doc)
        assert "| A | B |" in result
        assert "| --- | --- |" in result
        assert "| 1 | 2 |" in result

    def test_table_with_math(self):
        doc = Document(
            blocks=[
                Table(
                    headers=[TableCell(children=[Text("Metric")])],
                    rows=[[TableCell(children=[InlineMath(latex="x^2")])]],
                    alignments=[TableAlignment.NONE],
                )
            ]
        )
        result = render_markdown(doc)
        assert "$x^2$" in result


class TestListRendering:
    def test_unordered(self):
        doc = Document(
            blocks=[
                List(
                    ordered=False,
                    items=[
                        ListItem(children=[Paragraph(children=[Text("A")])]),
                        ListItem(children=[Paragraph(children=[Text("B")])]),
                    ],
                )
            ]
        )
        result = render_markdown(doc)
        assert "- A" in result
        assert "- B" in result

    def test_ordered(self):
        doc = Document(
            blocks=[
                List(
                    ordered=True,
                    items=[
                        ListItem(children=[Paragraph(children=[Text("First")])]),
                        ListItem(children=[Paragraph(children=[Text("Second")])]),
                    ],
                )
            ]
        )
        result = render_markdown(doc)
        assert "1. First" in result
        assert "2. Second" in result


class TestThematicBreakRendering:
    def test_hr(self):
        doc = Document(blocks=[ThematicBreak()])
        result = render_markdown(doc)
        assert "---" in result


class TestFrontMatterRendering:
    def test_with_metadata(self):
        doc = Document(
            metadata=Metadata(title="Test", author="User"),
            blocks=[Heading(level=1, children=[Text("Hello")])],
        )
        result = render_markdown(doc)
        assert "---" in result
        assert "title: Test" in result
        assert "author: User" in result

    def test_without_metadata(self):
        doc = Document(blocks=[Heading(level=1, children=[Text("Hello")])])
        result = render_markdown(doc)
        # Should not have front matter
        assert not result.startswith("---")


class TestTrailingNewline:
    def test_ends_with_newline(self):
        doc = Document(blocks=[Paragraph(children=[Text("Hello")])])
        result = render_markdown(doc)
        assert result.endswith("\n")
