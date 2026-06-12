# Current Task

## Prompt 35: Extract tracker delete/edit helpers

**Status:** In progress

**What I'm doing:**
In `main.py`, extracting `_tracker_delete(company, role)` and `_tracker_edit(company, role, field, value)` from the `tracker()` command. Keeping the single Typer command entry point but delegating to the new helpers.

**Next step:**
Edit `main.py`, run syntax check, commit with message `[Prompt 35] Extract tracker delete/edit helpers`, and push.

**Blockers:** None.
