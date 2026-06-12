# Current Task

## Step 18 — Phase D: Integration smoke tests

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Adding integration smoke tests to `tests/test_cli.py` that:
- Run `apply --dry-run` and assert no `.txt` resume or cover-letter files are written in `output/`
- Run a full mocked `apply` (without `--dry-run`) and assert `.pdf` and `.docx` files are created

**Next:** CI compatibility (Step 19).
