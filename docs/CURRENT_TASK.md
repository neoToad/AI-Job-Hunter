# Current Task

## Step 9 — Phase B: Update Streamlit resume UI

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `app.py` to:
- Store `saved_paths` in session state after pipeline completion
- Replace the editable "Tailored Resume" text area with a download button for the `.pdf`
- Keep a read-only preview of the resume dict using `st.json` or formatted markdown

**Next:** Wire DOCX rendering into pipeline (Step 10).
