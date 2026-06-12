"""Small helper functions used across the CLI."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import typer
from rich.console import Console

_console = Console()


def handle_error(message: str, hint: str = "") -> None:
    """Print a user-friendly error message and exit with code 1.

    Args:
        message: The main error text.
        hint: Optional remediation hint printed in dim text.
    """
    _console.print(f"[bold red]✗ {message}[/bold red]")
    if hint:
        _console.print(f"[dim]{hint}[/dim]")
    raise typer.Exit(1)


def make_slug(company: str, role: str, today: date | None = None) -> str:
    """Return a safe filename slug: {company}_{role}_{date}.txt.

    Cleaning rules:
    - lowercased
    - slashes (``/``, ``\\``) become dashes
    - all other non-alphanumeric runs become underscores
    - leading/trailing underscores are stripped
    """

    def _clean(s: str) -> str:
        s = s.lower()
        s = s.replace("/", "-").replace("\\", "-")
        s = re.sub(r"[^a-z0-9]+", "_", s)
        return s.strip("_")

    date_str = (today or date.today()).isoformat()
    return f"{_clean(company)}_{_clean(role)}_{date_str}.txt"
