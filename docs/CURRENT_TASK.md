# Current Task

## Step 10: Test `utils/tracker.py`

**Status:** In progress

**What I'm doing:**
- Created `tests/test_tracker.py` with 14 tests covering:
  - `add_application` date logic and empty validation
  - `application_exists` case-insensitive matching and missing file
  - `delete_application` success and not-found cases
  - `edit_application` editable field update and non-editable rejection
  - `update_status` valid change and invalid status
  - `get_followups_due` filtering by date and status
  - `show_tracker` on empty tracker
- **Improvement:** Fixed `show_tracker` in `utils/tracker.py` to skip the header row when iterating, preventing the header from being counted as a data row and ensuring the empty-tracker message prints correctly.

**Next step:** Commit and push, then move to Step 11 (Test `chains/analyzer.py`).
