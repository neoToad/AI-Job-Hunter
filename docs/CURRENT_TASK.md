# Current Task

## Step 5: Validate `--file` path is actually a file

**Status:** In progress

**What I'm doing:**
- In `job_search_tool/main.py`, `get_job_description` already checks `file.is_file()`, but it uses `handle_error()` instead of the Typer-native `typer.BadParameter`.
- Updating the check to raise `typer.BadParameter` so Typer prints a clean validation error before invoking the command.

**Next step:** Commit and push, then move to Step 6 (Add docstring to `first_run_check`).
