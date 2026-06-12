# Current Task

## Step 11 — Phase C: Update CLI output labels for cover letter

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** The `apply()` summary panel in `main.py` already displays the cover-letter path dynamically; since `cl_out` now ends in `.docx` (Step 10), the panel implicitly references `.docx` without further code changes. No hardcoded `.txt` references remain in `main.py`.

**Next:** Update Streamlit cover letter UI in `app.py` (Step 12).
