# Current Task

## Step 15: Add CI workflow

**Status:** In progress

**What I'm doing:**
- Creating `.github/workflows/test.yml` as specified in the testing plan.
- The workflow runs on push to `main`/`feature/*` and on PRs to `main`, installing dependencies and running `pytest tests/ -v -m "not ollama"`.
- Just ran the full test suite locally: **35 passed, 1 warning**.

**Next step:** Commit and push, then finalize the build.
