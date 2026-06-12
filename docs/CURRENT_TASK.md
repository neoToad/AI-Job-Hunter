# Current Task

## Step 14 — Phase D: Unit test `render_resume_pdf`

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Creating `tests/test_renderers.py` with a test that:
- Mocks `pdfkit.from_string`
- Asserts output file exists and has `.pdf` extension when passed a dummy dict

**Next:** Unit test `render_cover_letter_docx` (Step 15).
