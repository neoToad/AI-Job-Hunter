"""Tests for `utils/renderers`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from utils.renderers import render_cover_letter_docx, render_resume_pdf


_DUMMY_RESUME = {
    "contact": {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "location": "NYC",
        "linkedin": "linkedin.com/in/janedoe",
    },
    "summary": "Experienced Python developer.",
    "experience": [
        {
            "title": "Senior Dev",
            "company": "Acme",
            "dates": "2020-2024",
            "bullets": ["Built APIs", "Led team"],
        }
    ],
    "education": [
        {"degree": "BS CS", "school": "State U", "dates": "2016-2020"}
    ],
    "skills": ["Python", "Django", "AWS"],
}


class TestRenderResumePdf:
    def test_render_resume_pdf_creates_pdf(self, tmp_path: Path) -> None:
        """Mock pdfkit and assert a .pdf file is created."""
        out_path = tmp_path / "resume"

        with patch("pdfkit.from_string") as mock_pdfkit:
            render_resume_pdf(_DUMMY_RESUME, out_path)

        # pdfkit should have been called with HTML content and the target path
        mock_pdfkit.assert_called_once()
        html, path_arg = mock_pdfkit.call_args[0]
        assert path_arg == str(out_path.with_suffix(".pdf"))
        assert "<!DOCTYPE html>" in html

    def test_render_resume_pdf_fallback_when_pdfkit_missing(self, tmp_path: Path) -> None:
        """Fall back to .txt when pdfkit raises an exception."""
        out_path = tmp_path / "resume"

        with patch("pdfkit.from_string", side_effect=OSError("wkhtmltopdf not found")):
            render_resume_pdf(_DUMMY_RESUME, out_path)

        txt_path = out_path.with_suffix(".txt")
        assert txt_path.exists()
        content = txt_path.read_text(encoding="utf-8")
        assert "Jane Doe" in content
        assert "EXPERIENCE" in content

