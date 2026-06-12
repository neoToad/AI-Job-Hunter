"""Resume PDF parser.

Provides :func:`parse_resume` to extract the full text content of a
PDF resume (one block per page) and :func:`preview_resume` to return a
short snippet of that text for quick verification.

Also provides :func:`get_resume_text` which caches parsed text to disk
so the expensive PDF extraction only runs when the file changes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

from utils.console import console


def parse_resume(path: Path) -> str:
    """Extract all text from a PDF resume.

    Pages are joined with double newlines. Raises ``FileNotFoundError``
    when the path does not exist and ``ValueError`` when no text could
    be extracted from any page. If an individual page returns no text
    (likely image-based), a rich-formatted warning is printed but
    extraction continues for the remaining pages.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Resume PDF not found: {path}")

    pages_text: list[str] = []
    empty_pages: list[int] = []

    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                empty_pages.append(index)
            pages_text.append(text)

    for page_num in empty_pages:
        console.print(
            f"[bold yellow]Warning:[/] page {page_num} of {path.name} "
            f"returned no text — it may be image-based and require OCR."
        )

    joined = "\n\n".join(pages_text)
    if not joined.strip():
        raise ValueError(
            f"No text could be extracted from {path}. "
            "The PDF may be image-based — OCR may be required."
        )

    return joined


def _get_cache_paths(pdf_path: Path) -> tuple[Path, Path]:
    """Return (text_cache_path, meta_cache_path) for a given PDF."""
    parent = pdf_path.parent
    text_cache = parent / "resume_cache.txt"
    meta_cache = parent / ".resume_cache_meta.json"
    return text_cache, meta_cache


def get_resume_text(path: Path) -> str:
    """Return the full text of the resume, using a disk cache when valid.

    The parsed text is written to ``resume/resume_cache.txt`` (or the
    parent directory of the PDF). A sidecar JSON file stores the PDF's
    last-modified timestamp. If the PDF has not changed since the last
    parse, the cached text is returned instantly. Otherwise the PDF is
    re-parsed and the cache is refreshed.

    Args:
        path: Path to the resume PDF.

    Returns:
        The full extracted resume text.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If no text could be extracted.
    """
    path = Path(path)
    text_cache, meta_cache = _get_cache_paths(path)

    current_mtime = path.stat().st_mtime

    if text_cache.exists() and meta_cache.exists():
        try:
            meta = json.loads(meta_cache.read_text(encoding="utf-8"))
            cached_mtime = meta.get("mtime")
            if cached_mtime == current_mtime:
                return text_cache.read_text(encoding="utf-8")
        except (OSError, ValueError, KeyError):
            pass  # Cache invalid or unreadable; fall through to re-parse

    text = parse_resume(path)
    try:
        text_cache.write_text(text, encoding="utf-8")
        meta_cache.write_text(
            json.dumps({"path": str(path), "mtime": current_mtime}),
            encoding="utf-8",
        )
    except OSError:
        pass  # Cache write is best-effort; do not fail the user

    return text


def preview_resume(path: Path, chars: int = 500) -> str:
    """Return a short preview of the parsed resume text.

    Useful for verifying that parsing worked end-to-end without dumping
    the entire resume to the console. Returns at most ``chars`` characters
    of the parsed text, stripped of leading/trailing whitespace.
    """
    text = get_resume_text(path)
    return text.strip()[:chars]
