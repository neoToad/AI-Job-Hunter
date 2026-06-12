# Current Task

## Step 9: Test `utils/resume_parser.py`

**Status:** In progress

**What I'm doing:**
- Created `tests/test_resume_parser.py` with tests for:
  - Multi-page text PDF (mocked `pdfplumber`)
  - Missing file raises `FileNotFoundError`
  - Empty PDF raises `ValueError`
  - Image-based page prints warning but continues
  - Preview length cap

**Next step:** Commit and push, then move to Step 10 (Test `utils/tracker.py`).
