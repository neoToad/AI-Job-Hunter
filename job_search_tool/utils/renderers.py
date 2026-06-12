"""Output renderers for resumes and cover letters.

Provides two high-level helpers:
- ``render_resume_pdf`` – renders a structured resume dict through a Jinja2
  template and converts the resulting HTML to PDF via pdfkit.
- ``render_cover_letter_docx`` – writes a plain-text cover letter into a
  formatted Microsoft Word document via python-docx.

Both functions fall back gracefully to plain ``.txt`` files when their
respective third-party binary / library is missing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def render_resume_pdf(structured_resume: dict[str, Any], path: Path) -> None:
    """Render *structured_resume* to a PDF file via Jinja2 + pdfkit.

    If ``pdfkit`` or the ``wkhtmltopdf`` binary is unavailable, a ``.txt``
    file is written instead so the pipeline never crashes on missing
    dependencies.

    Args:
        structured_resume: Dictionary with keys ``contact``, ``summary``,
            ``experience``, ``education``, ``skills``.
        path: Destination file path.  Should end in ``.pdf``; if it does
            not the extension is replaced automatically.
    """
    try:
        import jinja2
        import pdfkit
    except ImportError as exc:
        _fallback_txt(path, _resume_to_text(structured_resume))
        return

    # Ensure the correct extension
    if path.suffix.lower() != ".pdf":
        path = path.with_suffix(".pdf")

    template_path = Path(__file__).resolve().parent.parent / "templates" / "resume.html"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path.name)
    html = template.render(resume=structured_resume)

    try:
        pdfkit.from_string(html, str(path))
    except Exception:
        # pdfkit raises OSError when wkhtmltopdf is missing.
        _fallback_txt(path, _resume_to_text(structured_resume))


def render_cover_letter_docx(text: str, path: Path) -> None:
    """Write *text* into a formatted ``.docx`` cover letter.

    If ``python-docx`` is unavailable, a ``.txt`` file is written instead.

    Args:
        text: The cover letter prose. Paragraphs are split on double
            newlines (``\\n\\n``).
        path: Destination file path.  Should end in ``.docx``; if it does
            not the extension is replaced automatically.
    """
    try:
        from docx import Document
        from docx.shared import Inches, Pt
    except ImportError:
        _fallback_txt(path, text)
        return

    # Ensure the correct extension
    if path.suffix.lower() != ".docx":
        path = path.with_suffix(".docx")

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    for para in text.split("\n\n"):
        stripped = para.strip()
        if stripped:
            p = doc.add_paragraph(stripped)
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.line_spacing = 1.15

    doc.save(path)


def _fallback_txt(path: Path, text: str) -> None:
    """Write *text* to a ``.txt`` version of *path*.

    Strips any existing extension and appends ``.txt`` so the user gets
    a readable file even when the primary renderer is unavailable.
    """
    txt_path = path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")


def _resume_to_text(resume: dict[str, Any]) -> str:
    """Flatten a structured resume dict into plain text for fallback mode."""
    lines: list[str] = []

    contact = resume.get("contact", {})
    if contact:
        lines.append(contact.get("name", ""))
        lines.append(
            " | ".join(
                str(v) for k, v in contact.items() if k != "name" and v
            )
        )
        lines.append("")

    summary = resume.get("summary", "")
    if summary:
        lines.append("SUMMARY")
        lines.append(summary)
        lines.append("")

    experience = resume.get("experience", [])
    if experience:
        lines.append("EXPERIENCE")
        for entry in experience:
            lines.append(
                f"{entry.get('title', '')} — {entry.get('company', '')} ({entry.get('dates', '')})"
            )
            for bullet in entry.get("bullets", []):
                lines.append(f"  • {bullet}")
            lines.append("")

    education = resume.get("education", [])
    if education:
        lines.append("EDUCATION")
        for entry in education:
            lines.append(
                f"{entry.get('degree', '')} — {entry.get('school', '')} ({entry.get('dates', '')})"
            )
        lines.append("")

    skills = resume.get("skills", [])
    if skills:
        lines.append("SKILLS")
        lines.append(", ".join(str(s) for s in skills))
        lines.append("")

    return "\n".join(lines)
