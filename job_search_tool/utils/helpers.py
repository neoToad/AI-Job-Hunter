"""Small helper functions used across the CLI."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import typer
from bs4 import BeautifulSoup
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
        return s.strip("_")[:50]

    date_str = (today or date.today()).isoformat()
    return f"{_clean(company)}_{_clean(role)}_{date_str}.txt"


_URL_CACHE_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "url_cache.json"


def fetch_url_text(url: str, timeout: int = 10) -> str:
    """Fetch a URL, extract readable text, and cache the result for 24 hours.

    Args:
        url: The URL to fetch. Must start with ``http://`` or ``https://``.
        timeout: Request timeout in seconds.

    Returns:
        Extracted plain text from the page body.

    Raises:
        requests.RequestException: If the request fails.
    """
    now = datetime.now(timezone.utc)

    # Check cache
    if _URL_CACHE_PATH.exists():
        try:
            cache: dict[str, dict[str, str]] = json.loads(
                _URL_CACHE_PATH.read_text(encoding="utf-8")
            )
            entry = cache.get(url)
            if entry:
                cached_at = datetime.fromisoformat(entry["cached_at"])
                if now - cached_at < timedelta(hours=24):
                    return entry["text"]
        except (OSError, ValueError, KeyError):
            pass  # Cache unreadable; fall through to fetch

    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    for tag_name in ("script", "style", "nav", "header", "footer"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    # Write cache (best-effort)
    try:
        cache = {}
        if _URL_CACHE_PATH.exists():
            cache = json.loads(_URL_CACHE_PATH.read_text(encoding="utf-8"))
        cache[url] = {"text": cleaned, "cached_at": now.isoformat()}
        _URL_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except OSError:
        pass

    return cleaned
