# Current Task

## Step 10 — Phase C: Wire DOCX rendering into pipeline

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `pipelines.py` to:
- Import `render_cover_letter_docx` from `utils.renderers`
- Change `cl_out` extension to `.docx`
- Replace `write_text()` for the cover letter with `render_cover_letter_docx()`

**Next:** Update CLI output labels for cover letter in `main.py` (Step 11).
