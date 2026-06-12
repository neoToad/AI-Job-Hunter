# Current Task

## Prompt 34: Break apply() into sub-functions

**Status:** In progress

**What I'm doing:**
Refactoring `main.py:apply()` into four private helpers as specified in the refactor plan:
- `_gather_inputs(file, url)` — parse resume + get job description + validate
- `_run_analysis(resume_text, job_description)` — analyze + display, returns `JobAnalysis`
- `_run_tailoring_and_cover_letter(analysis, resume_text, job_description, skip_tailor)` — returns `(tailored_resume, cover_letter)`
- `_save_outputs(tailored_resume, cover_letter, analysis)` — write files + prompt for source/notes + update tracker + print summary

**Next step:**
Edit `main.py`, run syntax check, commit with message `[Prompt 34] Break apply() into sub-functions`, and push.

**Blockers:** None.
