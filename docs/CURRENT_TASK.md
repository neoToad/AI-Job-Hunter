# Current Task

## Step 16 — Phase D: Unit test `tailor_resume` with JSON output

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Adding an explicit test to `tests/test_tailorer.py` that:
- Uses `FakeListChatModel` returning valid JSON
- Asserts the returned dict contains the expected top-level keys: contact, summary, experience, education, skills

**Next:** Update tracker tests (Step 17).
