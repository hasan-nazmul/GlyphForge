"""Renderer registry for unified format lookup."""

from __future__ import annotations

from typing import Type, Union

from glyphforge.config import OutputFormat
from glyphforge.renderers.base import BaseRenderer


class RendererRegistry:
    """Registry mapping format identifiers to renderer classes/instances."""

    _registry: dict[str, type[BaseRenderer] | BaseRenderer] = {}

    @classmethod
    def register(
        cls,
        format_key: Union[str, OutputFormat],
        renderer: type[BaseRenderer] | BaseRenderer,
    ) -> None:
        """Register a renderer class or instance for *format_key*."""
        key = str(format_key.value if isinstance(format_key, OutputFormat) else format_key).lower()
        cls._registry[key] = renderer

    @classmethod
    def get(cls, format_key: Union[str, OutputFormat]) -> BaseRenderer:
        """Retrieve an initialized renderer for *format_key*.

        Raises
        ------
        KeyError
            If no renderer is registered for *format_key*.
        """
        key = str(format_key.value if isinstance(format_key, OutputFormat) else format_key).lower()
        if key not in cls._registry:
            raise KeyError(
                f"No renderer registered for format '{format_key}'. "
                f"Supported formats: {', '.join(sorted(cls._registry.keys()))}"
            )
        entry = cls._registry[key]
        if isinstance(entry, type):
            return entry()
        return entry

    @classmethod
    def has(cls, format_key: Union[str, OutputFormat]) -> bool:
        """Return True if a renderer is registered for *format_key*."""
        key = str(format_key.value if isinstance(format_key, OutputFormat) else format_key).lower()
        return key in cls._registry

    @classmethod
    def supported_formats(cls) -> list[str]:
        """Return list of supported format keys."""
        return sorted(cls._registry.keys())
