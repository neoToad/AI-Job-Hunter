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


_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Return a filesystem-safe version of *name*.

    Rules:
    - Strip path separators (``/``, ``\\``, ``..``)
    - Remove characters unsafe for filenames: ``< > : \" | ? *`` and control chars
    - Collapse multiple unsafe runs to a single underscore
    - Strip leading/trailing dots, spaces, and underscores
    - Truncate to *max_length*
    - Fall back to ``"unknown"`` if the result is empty
    - Avoid Windows reserved names (CON, PRN, AUX, NUL, COM1–9, LPT1–9)
    """
    # Strip path traversal patterns
    cleaned = name.replace("..", "")
    cleaned = cleaned.replace("/", "-").replace("\\", "-")

    # Remove unsafe characters
    cleaned = re.sub(r"[<>:\"|?*\x00-\x1f]", "", cleaned)

    # Collapse remaining non-alphanumeric (except dash and dot) to underscore
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", cleaned)

    # Strip leading/trailing unsafe chars
    cleaned = cleaned.strip(" ._-")

    # Truncate
    cleaned = cleaned[:max_length]

    # Avoid Windows reserved names (case-insensitive)
    if cleaned.upper() in _WINDOWS_RESERVED:
        cleaned = f"{cleaned}_file"

    if not cleaned:
        cleaned = "unknown"

    return cleaned


def make_slug(company: str, role: str, today: date | None = None) -> str:
    """Return a safe filename slug: {company}_{role}_{date}.txt."""
    date_str = (today or date.today()).isoformat()
    return f"{sanitize_filename(company)}_{sanitize_filename(role)}_{date_str}.txt"


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

    # Cap length before passing to the LLM to avoid massive token usage
    _MAX_URL_TEXT = 8000
    if len(cleaned) > _MAX_URL_TEXT:
        cleaned = cleaned[:_MAX_URL_TEXT]

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
