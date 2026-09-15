"""YAML front matter extraction.

Extracts and removes YAML front matter delimited by ``---`` from the top of
a document, returning both the parsed Metadata and the remaining body text.
"""

from __future__ import annotations

import re

import yaml

from glyphforge.model.document import Metadata

_FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\n(.*?\n)---[ \t]*\n",
    re.DOTALL,
)


def extract_frontmatter(text: str) -> tuple[Metadata, str]:
    """Extract YAML front matter from the beginning of *text*.

    Returns
    -------
    (metadata, body)
        *metadata* contains the parsed fields.  *body* is the document text
        with the front matter block removed.
    """
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return Metadata(), text

    raw_yaml = match.group(1)
    body = text[match.end():]

    try:
        data = yaml.safe_load(raw_yaml)
    except yaml.YAMLError:
        # Malformed YAML — treat the whole thing as body, preserving content.
        return Metadata(), text

    if not isinstance(data, dict):
        return Metadata(), text

    metadata = Metadata(
        title=_str_or_none(data.get("title")),
        author=_str_or_none(data.get("author")),
        date=_str_or_none(data.get("date")),
        subject=_str_or_none(data.get("subject")),
        tags=_str_list(data.get("tags")),
        raw_frontmatter=raw_yaml.rstrip("\n"),
    )
    return metadata, body


def _str_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
