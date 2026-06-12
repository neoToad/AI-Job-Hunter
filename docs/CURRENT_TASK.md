# Current Task

## Step 8: Create test structure and `conftest.py`

**Status:** In progress

**What I'm doing:**
- Created `tests/` directory at the repo root with `conftest.py` containing fixtures: `sample_resume_text`, `sample_job_description`, `sample_job_analysis`, `tmp_tracker`, and `mock_llm`.
- Created `pyproject.toml` at the repo root to configure `pythonpath = ["job_search_tool"]` so tests can import project modules using the same absolute paths the CLI and Streamlit use.

**Next step:** Commit and push, then move to Step 9 (Test `utils/resume_parser.py`).
