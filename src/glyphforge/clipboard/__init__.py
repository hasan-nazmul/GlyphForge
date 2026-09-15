"""Linux clipboard detection and ingestion."""

from glyphforge.clipboard.linux import ClipboardError, read_clipboard, write_clipboard

__all__ = ["ClipboardError", "read_clipboard", "write_clipboard"]
