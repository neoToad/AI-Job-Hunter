# Current Task

## Step 13 — Phase C: Prune tracker cover-letter column

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `utils/tracker.py` and all callers to:
- Remove `"Cover Letter Path"` from `_HEADERS`
- Drop `cover_letter_path` parameter from `add_application()`
- Update pipeline in `pipelines.py` to stop passing the parameter
- Update tests and fixtures that reference the column
- Verify old trackers with orphaned column still render

**Next:** Unit test `render_resume_pdf` (Step 14).
