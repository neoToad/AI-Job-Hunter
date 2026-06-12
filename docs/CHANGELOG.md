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

## Step 9 — feat(ui): replace editable resume text area with PDF download button in Streamlit

- Stored `saved_paths` in Streamlit session state after pipeline completion.
- Replaced the "Tailored Resume" editable text area with a `st.download_button` for the generated `.pdf`.
- Added fallback info message when the PDF file is not found.

## Step 10 — feat(pipelines): wire DOCX cover letter rendering into apply pipeline

- Imported `render_cover_letter_docx` and changed `cl_out` extension to `.docx`.
- Replaced `write_text()` for cover letters with `render_cover_letter_docx()`.

## Step 11 — docs(main): confirm CLI summary panel implicitly references .docx

- The `apply()` summary panel in `main.py` already uses dynamic paths.
- Since `cl_out` now carries the `.docx` extension (Step 10), no further label changes were required.

## Step 12 — feat(ui): add DOCX download button for cover letter in Streamlit

- Kept the "Cover Letter" editable text area as a preview.
- Added a `st.download_button` for the `.docx` file below the text area.
- Used correct MIME type `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.

## Step 13 — refactor(tracker): remove Cover Letter Path column and parameter

- Removed `"Cover Letter Path"` from `_HEADERS` and `_EDITABLE_FIELDS`.
- Dropped `cover_letter_path` parameter from `add_application()`.
- Updated all callers in `pipelines.py`, `conftest.py`, `test_tracker.py`, and `test_cli.py`.
- `show_tracker` now reads headers from the worksheet itself, gracefully handling old trackers with orphaned columns.

<!-- New entries go below this line -->

