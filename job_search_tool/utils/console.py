"""Shared Rich console singleton.

Utility modules that need to print warnings or tables can import the single
``console`` instance from here instead of creating their own. This keeps
output styling consistent and avoids multiple Console objects writing to the
same terminal.
"""

from __future__ import annotations

from rich.console import Console

console = Console()
