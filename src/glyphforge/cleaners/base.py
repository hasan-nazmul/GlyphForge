"""Abstract Cleaner interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Cleaner(ABC):
    """Base interface for document text cleaners.

    Cleaners operate on raw text *before* parsing to fix common issues
    in messy LLM output.
    """

    @abstractmethod
    def clean(self, text: str) -> str:
        """Clean *text* and return the normalized version."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this cleaner."""
        ...
