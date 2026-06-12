# Current Task

## Prompt 32: Extract resume parse + error handling in CLI

**Status:** In progress

**What I'm doing:**
In `main.py`, creating `_parse_resume_for_cli() -> str` that wraps `parse_resume(config.RESUME_PATH)` with the `console.status("[bold green]Parsing resume...")` spinner and identical `FileNotFoundError` / `ValueError` handling. Then replacing the duplicated blocks in `analyze()` and `apply()` with a call to this new helper.

**Next step:**
Edit `main.py`, run a quick smoke test on the import, commit with message `[Prompt 32] Extract resume parse + error handling in CLI`, and push.

**Blockers:** None.
