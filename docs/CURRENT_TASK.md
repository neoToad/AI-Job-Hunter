# Current Task

## Completing remaining refactor_plan.md items

**Status:** In progress

**What I'm doing:**
- Item 3.3: Create `utils/console.py` singleton and update `utils/tracker.py`, `utils/resume_parser.py`, and `config.py` to use it.
- Item 6.1: Extract shared resume parsing helper — remove redundant `exists()` checks from `main.py` and `app.py` since `get_resume_text()` already raises uniform `FileNotFoundError` / `ValueError`.

**Next step:**
Edit files, run syntax checks, commit, and push. Then update `refactor_plan.md` to reflect completion.

**Blockers:** None.
