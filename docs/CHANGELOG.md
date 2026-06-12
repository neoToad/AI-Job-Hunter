# Changelog

## [Unreleased]

Branch: `feature/job-search-output-formats`

---

## Step 1 — feat(utils): add shared renderers module with PDF/DOCX renderers and graceful .txt fallback

- Created `job_search_tool/utils/renderers.py` with `render_resume_pdf()` and `render_cover_letter_docx()`.
- Both functions gracefully fall back to `.txt` if required libraries (`pdfkit`/`wkhtmltopdf` or `python-docx`) are missing.
- Added `_resume_to_text()` helper to flatten a structured resume dict into plain text for fallback mode.

## Step 2 — feat(templates): add professional single-column resume HTML template

- Created `job_search_tool/templates/resume.html` with a clean, single-column layout.
- Sections: contact header, summary, experience (with bullets), education, skills.
- CSS includes font sizing, spacing, and `page-break-inside: avoid` for experience blocks.

## Step 3 — chore(deps): add Jinja2, pdfkit, and python-docx to requirements.txt

- Added `Jinja2==3.1.6`, `pdfkit==1.0.0`, and `python-docx==1.1.2`.
- Added comment documenting the non-Pip `wkhtmltopdf` binary prerequisite.

## Step 4 — feat(chains): add TailoredResume and ExperienceEntry Pydantic models

- Added `ExperienceEntry` and `TailoredResume` Pydantic models in `chains/tailorer.py`.
- Models mirror the planned JSON schema: contact, summary, experience, education, skills.

## Step 6 — feat(chains): refactor tailor_resume to return structured JSON dict

- Replaced `StrOutputParser` with `JsonOutputParser` using `TailoredResume` model.
- Added `OutputParserException` handling that raises `ValueError("AI returned unexpected format...")`.
- Updated `tailorer_system.txt` to remove inline JSON example (avoids LangChain f-string curly-brace conflicts).
- Updated `test_tailorer.py` to assert dict return values and test malformed JSON path.

## Step 8 — refactor(main): update CLI filenames to support .pdf output

- Removed hardcoded `.txt` extension from `make_slug()` in `utils/helpers.py`; callers now append their own extension.
- Updated `followup` command in `main.py` to explicitly append `.txt` when saving follow-up emails.
- The `apply()` summary panel already displays the correct extension via the dynamic path.

<!-- New entries go below this line -->

