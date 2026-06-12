# Current Task

## Step 6 — Phase B: Refactor `tailor_resume` chain

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating `chains/tailorer.py` to:
- Use `JsonOutputParser` with `TailoredResume` Pydantic model
- Catch `OutputParserException` and raise `ValueError` with friendly retry message
- Return a structured dict instead of a plain string
- Update the existing test to work with the new JSON response

**Next:** Wire PDF rendering into `pipelines.py` (Step 7).
