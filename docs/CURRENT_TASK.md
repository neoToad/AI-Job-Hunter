# Current Task

## Prompt 36: Standardize load_workbook read-only usage

**Status:** In progress

**What I'm doing:**
In `utils/tracker.py`, ensuring `read_only=True` is used for pure reads (`application_exists`, `show_tracker`, `get_followups_due`) and explicitly opening read-write for mutations (`update_status`, `delete_application`, `edit_application`). Also adding a brief comment documenting the pattern. `add_application` uses `_get_or_create_workbook` which already handles creation properly.

**Next step:**
Edit `utils/tracker.py`, run syntax check, commit with message `[Prompt 36] Standardize load_workbook read-only usage`, and push.

**Blockers:** None.
