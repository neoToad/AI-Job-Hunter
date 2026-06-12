"""Tests for `utils/resume_parser`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from utils.resume_parser import parse_resume, preview_resume


# ---------------------------------------------------------------------------
# parse_resume
# ---------------------------------------------------------------------------


def test_parse_resume_multi_page(tmp_path: Path) -> None:
    """Return full text from a multi-page text-based PDF."""
    dummy_pdf = tmp_path / "resume.pdf"
    dummy_pdf.write_bytes(b"%PDF-dummy")

    page1 = MagicMock()
    page1.extract_text.return_value = "Page one text"
    page2 = MagicMock()
    page2.extract_text.return_value = "Page two text"

    mock_pdf = MagicMock()
    mock_pdf.pages = [page1, page2]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)

    with patch("utils.resume_parser.pdfplumber.open", return_value=mock_pdf):
        result = parse_resume(dummy_pdf)

    assert result == "Page one text\n\nPage two text"


def test_parse_resume_file_not_found() -> None:
    """Raise FileNotFoundError when the PDF does not exist."""
    with pytest.raises(FileNotFoundError, match="Resume PDF not found"):
        parse_resume("/nonexistent/path/resume.pdf")


def test_parse_resume_empty_pdf(tmp_path: Path) -> None:
    """Raise ValueError when every page returns no text."""
    dummy_pdf = tmp_path / "empty.pdf"
    dummy_pdf.write_bytes(b"%PDF-dummy")

    page = MagicMock()
    page.extract_text.return_value = ""

    mock_pdf = MagicMock()
    mock_pdf.pages = [page]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)

    with patch("utils.resume_parser.pdfplumber.open", return_value=mock_pdf):
        with pytest.raises(ValueError, match="No text could be extracted"):
            parse_resume(dummy_pdf)


def test_parse_resume_image_page_warning(tmp_path: Path, capsys) -> None:
    """Print a warning for image-based pages but continue extraction."""
    dummy_pdf = tmp_path / "mixed.pdf"
    dummy_pdf.write_bytes(b"%PDF-dummy")

    page1 = MagicMock()
    page1.extract_text.return_value = ""
    page2 = MagicMock()
    page2.extract_text.return_value = "Real text"

    mock_pdf = MagicMock()
    mock_pdf.pages = [page1, page2]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)

    with patch("utils.resume_parser.pdfplumber.open", return_value=mock_pdf):
        with patch("utils.resume_parser.console.print") as mock_print:
            result = parse_resume(dummy_pdf)

    assert result == "\n\nReal text"
    mock_print.assert_called_once()
    assert "page 1" in mock_print.call_args[0][0]
    assert "image-based" in mock_print.call_args[0][0]


# ---------------------------------------------------------------------------
# preview_resume
# ---------------------------------------------------------------------------


def test_preview_resume_length_cap(tmp_path: Path) -> None:
    """Return at most N characters."""
    dummy_pdf = tmp_path / "resume.pdf"
    dummy_pdf.write_bytes(b"%PDF-dummy")

    long_text = "A" * 1000
    page = MagicMock()
    page.extract_text.return_value = long_text

    mock_pdf = MagicMock()
    mock_pdf.pages = [page]
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)

    with patch("utils.resume_parser.pdfplumber.open", return_value=mock_pdf):
        preview = preview_resume(dummy_pdf, chars=50)

    assert len(preview) == 50
    assert preview == "A" * 50
