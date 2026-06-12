# Current Task

## Step 3: Add `st.session_state` gating for apply pipeline

**Status:** In progress

**What I'm doing:**
- In `job_search_tool/app.py`, fix `_clear_stale_state` to clear the correct session state keys for Full Application mode (`analysis`, `tailored_resume`, `cover_letter`, `apply_complete`).
- Add mode-change gating so that switching between "Analyze Job" and "Full Application" modes also clears cached results, preventing stale data from one mode appearing in the other.

**Next step:** Commit and push, then move to Step 4 (Add Windows reserved name check to `make_slug`).
