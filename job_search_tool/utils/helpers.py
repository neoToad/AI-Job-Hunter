"""Small helper functions used across the CLI."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path


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
