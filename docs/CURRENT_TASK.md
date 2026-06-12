# Current Task

## Step 7 — Phase B: Wire PDF rendering into pipeline

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `pipelines.py` to:
- Import `render_resume_pdf` from `utils.renderers`
- Change `resume_out` extension to `.pdf`
- Replace `write_text()` for the resume with `render_resume_pdf()` when tailoring is active
- Fall back to `.txt` when `skip_tailor=True` (original resume text is a string, not structured dict)

**Next:** Update CLI output labels in `main.py` (Step 8).
