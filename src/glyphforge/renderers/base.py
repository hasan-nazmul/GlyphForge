"""Base renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from glyphforge.model.document import Document


class BaseRenderer(ABC):
    """Abstract base for all output renderers."""

    @abstractmethod
    def render(self, document: Document, output_path: Path, **kwargs: Any) -> Path:
        """Render *document* and write the result to *output_path*.

        Parameters
        ----------
        document
            Document IR to render.
        output_path
            Destination file path.
        **kwargs
            Renderer-specific options (e.g. toc=True, theme="technical").

        Returns
        -------
        Path
            The path to the generated file.
        """
        ...

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Human-readable name of the output format (e.g. 'Markdown', 'HTML', 'PDF', 'DOCX')."""
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension including the dot (e.g. '.md', '.html', '.pdf', '.docx')."""
        ...
