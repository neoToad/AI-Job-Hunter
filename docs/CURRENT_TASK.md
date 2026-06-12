# Current Task

## Prompt 33: Extract _run_chain_with_spinner and standardize error handling

**Status:** In progress

**What I'm doing:**
Creating `_run_chain_with_spinner(description: str, fn: Callable[[], T]) -> T` in `main.py` that wraps the `Progress(SpinnerColumn(), TextColumn(...))` context and generic `ConnectionError` / `Exception` handling. Replacing the ~6 duplicated Progress blocks across `analyze()`, `apply()`, and `followup()`. Also auditing the file to standardize on `handle_error()` for fatal errors and `console.print(...)` + `raise typer.Exit(0)` for user aborts.

**Next step:**
Edit `main.py`, run syntax check, commit with message `[Prompt 33] Extract _run_chain_with_spinner and standardize error handling`, and push.

**Blockers:** None.
