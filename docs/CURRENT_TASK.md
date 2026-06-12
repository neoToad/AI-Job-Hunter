# Current Task

## Step 8 — Phase B: Update CLI output labels

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `main.py` and `utils/helpers.py` so the CLI output paths reflect the new formats:
- Fix `make_slug` to stop hardcoding `.txt` (callers now append their own extensions)
- Update follow-up save path in `main.py` to explicitly append `.txt`
- The `apply()` summary panel already shows the correct extension via the path object

**Next:** Update Streamlit resume UI in `app.py` (Step 9).
