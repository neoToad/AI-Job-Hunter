# Current Task

## Step 13: Test `config.py`

**Status:** In progress

**What I'm doing:**
- Created `tests/test_config.py` with tests for `validate_config`:
  - No warnings printed when config is valid (resume exists, model set, Ollama port open)
  - Warning printed when resume is missing
- Mocked `os.getenv`, socket checks, and `RESUME_PATH.exists` appropriately.

**Next step:** Commit and push, then move to Step 14 (Test CLI `main.py`).
