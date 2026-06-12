"""Integration tests for the Typer CLI in `main.py`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

import config
from main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------


def test_verify_exits_1_when_resume_missing(monkeypatch) -> None:
    """Exit with code 1 when the resume PDF is missing."""
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=False)))
    result = runner.invoke(app, ["verify"])
    assert result.exit_code == 1
    assert "Resume not found" in result.output


def test_verify_exits_0_when_valid(monkeypatch) -> None:
    """Exit with code 0 when the resume is parseable and Ollama is reachable."""
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=True)))

    with patch("main.preview_resume", return_value="John Doe — Python Developer..."):
        with patch("main.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "models": [{"name": config.OLLAMA_MODEL}]
            }
            mock_get.return_value.raise_for_status = MagicMock()
            result = runner.invoke(app, ["verify"])

    assert result.exit_code == 0
    assert "Resume OK" in result.output
    assert "Ollama OK" in result.output


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------


def test_analyze_with_file_exits_0(tmp_path: Path, monkeypatch) -> None:
    """Exit with code 0 when --file points to a valid job description."""
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=True)))

    jd_file = tmp_path / "jd.txt"
    jd_file.write_text(
        "We are hiring a Python Developer.\n"
        "Responsibilities:\n- Build APIs\n- Write tests\n"
        "Requirements:\n- 3+ years Python\n- Django experience\n"
        "- PostgreSQL\n- Docker\n",
        encoding="utf-8",
    )

    fake_analysis = MagicMock()
    fake_analysis.company = "Acme"
    fake_analysis.role = "Python Developer"
    fake_analysis.match_score = 85
    fake_analysis.recommendation = "apply"
    fake_analysis.summary = "Strong fit."
    fake_analysis.to_display_dict.return_value = {}

    with patch("main.get_resume_text", return_value="resume text"):
        with patch("main.analyze_job", return_value=fake_analysis):
            result = runner.invoke(app, ["analyze", "--file", str(jd_file)])

    assert result.exit_code == 0
    assert "Job Analysis" in result.output


# ---------------------------------------------------------------------------
# tracker
# ---------------------------------------------------------------------------


def test_tracker_show_empty_tracker(tmp_path: Path, monkeypatch) -> None:
    """Exit with code 0 when showing an empty tracker."""
    tracker_path = tmp_path / "tracker.xlsx"
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Applications"
    headers = [
        "Company",
        "Role",
        "Date Applied",
        "Source",
        "Match Score",
        "Status",
        "Follow-up Date",
        "Notes",
        "Cover Letter Path",
    ]
    ws.append(headers)
    wb.save(tracker_path)

    monkeypatch.setattr(config, "TRACKER_PATH", tracker_path)
    result = runner.invoke(app, ["tracker", "--show"])
    assert result.exit_code == 0


def test_tracker_delete_with_confirmation(tmp_path: Path, monkeypatch) -> None:
    """Exit with code 0 after confirming deletion of an existing entry."""
    tracker_path = tmp_path / "tracker.xlsx"
    from utils.tracker import add_application

    add_application(tracker_path, "Acme", "Engineer", "LinkedIn", 80, "")
    monkeypatch.setattr(config, "TRACKER_PATH", tracker_path)

    result = runner.invoke(app, ["tracker", "--delete", "--company", "Acme", "--role", "Engineer"], input="y\n")
    assert result.exit_code == 0
    assert "Deleted" in result.output


# ---------------------------------------------------------------------------
# apply — output format smoke tests
# ---------------------------------------------------------------------------


def test_apply_dry_run_writes_no_txt_files(tmp_path: Path, monkeypatch) -> None:
    """Run apply --dry-run and assert no .txt resume or cover-letter files appear."""
    output_dir = tmp_path / "output"
    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "TAILORED_RESUMES_DIR", output_dir / "tailored_resumes")
    monkeypatch.setattr(config, "COVER_LETTERS_DIR", output_dir / "cover_letters")
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=True)))
    monkeypatch.setattr(config, "TRACKER_PATH", tmp_path / "tracker.xlsx")

    jd_file = tmp_path / "jd.txt"
    jd_file.write_text(
        "We are hiring a Python Developer.\n"
        "Responsibilities:\n- Build APIs\n"
        "Requirements:\n- 3+ years Python\n",
        encoding="utf-8",
    )

    fake_analysis = MagicMock()
    fake_analysis.company = "Acme"
    fake_analysis.role = "Python Developer"
    fake_analysis.match_score = 85
    fake_analysis.recommendation = "apply"
    fake_analysis.summary = "Strong fit."
    fake_analysis.to_display_dict.return_value = {}

    with patch("main.get_resume_text", return_value="resume text"):
        with patch("main.analyze_job", return_value=fake_analysis):
            result = runner.invoke(app, ["apply", "--dry-run", "--file", str(jd_file)])

    assert result.exit_code == 0
    txt_files = list(output_dir.rglob("*.txt"))
    assert len(txt_files) == 0, f"Unexpected .txt files: {txt_files}"


def test_apply_creates_pdf_and_docx_not_txt(tmp_path: Path, monkeypatch) -> None:
    """Run a mocked apply and assert .pdf resume and .docx cover letter are created."""
    output_dir = tmp_path / "output"
    tailored_dir = output_dir / "tailored_resumes"
    cl_dir = output_dir / "cover_letters"
    monkeypatch.setattr(config, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "TAILORED_RESUMES_DIR", tailored_dir)
    monkeypatch.setattr(config, "COVER_LETTERS_DIR", cl_dir)
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=True)))
    monkeypatch.setattr(config, "TRACKER_PATH", tmp_path / "tracker.xlsx")

    jd_file = tmp_path / "jd.txt"
    jd_file.write_text(
        "We are hiring a Python Developer.\n"
        "Responsibilities:\n- Build APIs\n- Write tests\n"
        "Requirements:\n- 3+ years Python\n- Django experience\n"
        "- PostgreSQL\n- Docker\n",
        encoding="utf-8",
    )

    fake_analysis = MagicMock()
    fake_analysis.company = "Acme"
    fake_analysis.role = "Python Developer"
    fake_analysis.match_score = 85
    fake_analysis.recommendation = "apply"
    fake_analysis.summary = "Strong fit."
    fake_analysis.to_display_dict.return_value = {}

    fake_tailored = {
        "contact": {"name": "Jane"},
        "summary": "Dev",
        "experience": [],
        "education": [],
        "skills": ["Python"],
    }

    with patch("main.get_resume_text", return_value="resume text"):
        with patch("main.analyze_job", return_value=fake_analysis):
            with patch("pipelines.tailor_resume", return_value=fake_tailored):
                with patch("pipelines.generate_cover_letter", return_value="Dear Hiring Manager,"):
                    with patch("pipelines.render_resume_pdf") as mock_pdf:
                        with patch("pipelines.render_cover_letter_docx") as mock_docx:
                            # Provide input: y for confirm, empty for source, empty for notes
                            result = runner.invoke(
                                app,
                                ["apply", "--file", str(jd_file)],
                                input="y\n\n\n",
                            )

    assert result.exit_code == 0, f"Exit code: {result.exit_code}, output: {result.output}"
    assert mock_pdf.called, f"render_resume_pdf should have been called. Output: {result.output}"
    assert mock_docx.called, "render_cover_letter_docx should have been called"
    # Ensure no .txt files were created in the output dirs
    txt_files = list(output_dir.rglob("*.txt"))
    assert len(txt_files) == 0, f"Unexpected .txt files: {txt_files}"
