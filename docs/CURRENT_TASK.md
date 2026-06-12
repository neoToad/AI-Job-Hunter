# Current Task

## Step 1 — Phase A: Create `utils/renderers.py`

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Creating the shared renderer module with two functions:
- `render_resume_pdf(structured_resume: dict, path: Path) -> None`
- `render_cover_letter_docx(text: str, path: Path) -> None`

Each function includes graceful fallback to `.txt` if the required binary/library is missing.

**Next:** Create `templates/resume.html` (Step 2).
