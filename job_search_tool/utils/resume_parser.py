"""Resume PDF parser.

Provides :func:`parse_resume` to extract the full text content of a
PDF resume (one block per page) and :func:`preview_resume` to return a
short snippet of that text for quick verification.
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber
from rich.console import Console

_console = Console()


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
        _console.print(
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


def preview_resume(path: Path, chars: int = 500) -> str:
    """Return a short preview of the parsed resume text.

    Useful for verifying that parsing worked end-to-end without dumping
    the entire resume to the console. Returns at most ``chars`` characters
    of the parsed text, stripped of leading/trailing whitespace.
    """
    text = parse_resume(path)
    return text.strip()[:chars]
