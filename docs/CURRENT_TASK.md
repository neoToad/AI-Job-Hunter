# Current Task

## Step 7: Document unwrapped `ConnectionError` in chains

**Status:** In progress

**What I'm doing:**
- Add a note to the module-level docstrings in `chains/analyzer.py`, `chains/tailorer.py`, `chains/cover_letter.py`, and `chains/followup.py` stating that `.invoke()` calls are not wrapped and callers must handle connection errors.

**Next step:** Commit and push, then move to Phase B Step 8 (Create test structure and `conftest.py`).
