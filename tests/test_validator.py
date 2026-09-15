"""Tests for the document validator."""

from glyphforge.model.blocks import (
    CodeBlock,
    DisplayMath,
    Heading,
    Paragraph,
    Table,
    TableAlignment,
    TableCell,
)
from glyphforge.model.document import Document
from glyphforge.model.inlines import InlineMath, Text
from glyphforge.validation.validator import Severity, validate


class TestHeadingHierarchy:
    def test_valid_hierarchy(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("H1")]),
                Heading(level=2, children=[Text("H2")]),
                Heading(level=3, children=[Text("H3")]),
            ]
        )
        result = validate(doc)
        assert result.is_valid
        hierarchy_warnings = [i for i in result.issues if "hierarchy" in i.message.lower()]
        assert len(hierarchy_warnings) == 0

    def test_skipped_hierarchy(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("H1")]),
                Heading(level=3, children=[Text("H3")]),
            ]
        )
        result = validate(doc)
        hierarchy_warnings = [i for i in result.issues if "hierarchy" in i.message.lower()]
        assert len(hierarchy_warnings) == 1
        assert "H2" in hierarchy_warnings[0].message


class TestStatistics:
    def test_counts(self):
        doc = Document(
            blocks=[
                Heading(level=1, children=[Text("Title")]),
                Paragraph(children=[Text("Para"), InlineMath(latex="x")]),
                DisplayMath(latex="E=mc^2"),
                CodeBlock(code="print()", language="python"),
                Table(
                    headers=[TableCell(children=[Text("A")])],
                    rows=[],
                    alignments=[TableAlignment.NONE],
                ),
            ]
        )
        result = validate(doc)
        assert result.heading_count == 1
        assert result.inline_math_count == 1
        assert result.display_math_count == 1
        assert result.code_block_count == 1
        assert result.table_count == 1


class TestEmptyBlocks:
    def test_empty_code_block(self):
        doc = Document(blocks=[CodeBlock(code="", language="python")])
        result = validate(doc)
        warnings = [i for i in result.issues if "empty code" in i.message.lower()]
        assert len(warnings) == 1

    def test_empty_math_block(self):
        doc = Document(blocks=[DisplayMath(latex="")])
        result = validate(doc)
        warnings = [i for i in result.issues if "empty display math" in i.message.lower()]
        assert len(warnings) == 1


class TestEmptyDocument:
    def test_empty(self):
        doc = Document(blocks=[])
        result = validate(doc)
        warnings = [i for i in result.issues if "empty" in i.message.lower()]
        assert len(warnings) == 1


class TestTableValidation:
    def test_inconsistent_columns(self):
        doc = Document(
            blocks=[
                Table(
                    headers=[
                        TableCell(children=[Text("A")]),
                        TableCell(children=[Text("B")]),
                    ],
                    rows=[
                        [TableCell(children=[Text("1")])],  # Only 1 column, should be 2
                    ],
                    alignments=[TableAlignment.NONE, TableAlignment.NONE],
                )
            ]
        )
        result = validate(doc)
        col_warnings = [i for i in result.issues if "column" in i.message.lower()]
        assert len(col_warnings) == 1


class TestDemoDocument:
    def test_demo_validates(self, demo_md):
        from glyphforge.parser.markdown_parser import parse

        doc = parse(demo_md)
        result = validate(doc)
        assert result.is_valid
        assert result.heading_count > 0
        assert result.equation_count > 0
        assert result.code_block_count > 0
        assert result.table_count > 0
