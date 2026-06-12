"""Shared helpers for the chain modules."""

from __future__ import annotations

from pathlib import Path


def load_prompt(name: str) -> str:
    """Load a prompt template from the ``prompts/`` directory.

    Args:
        name: Filename of the prompt template (e.g. ``analyzer_system.txt``).

    Returns:
        The full text content of the prompt file.
    """
    return (Path(__file__).parent.parent / "prompts" / name).read_text()
