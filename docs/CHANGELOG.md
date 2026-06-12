# Changelog

## Build: Job Search Tool Follow-up Prompts (11–20)

Branch: `feature/job-search-followup`

---

### [Prompt 11] Fix output directory and init files
- Ensured `chains/__init__.py` and `utils/__init__.py` already exist (no changes needed).
- Updated `config.py` to create `data/` and `resume/` directories on import alongside existing output dirs.
- Wrapped output file save steps in `main.py` with `OSError`-specific try/except and a Rich-formatted hint.
- **Improvement beyond spec:** Used `OSError` instead of bare `Exception` for more precise error handling; added a hint about checking directory writability.

### [Prompt 12] Add first-run experience
- Added Typer `@app.callback()` in `main.py` that runs before every command.
- Checks for `resume/resume.pdf` and `.env`; prints friendly Rich Panel with setup steps if either is missing.
- Does not block execution so `verify` can still run and show detailed errors.
- **Improvement beyond spec:** Added `invoke_without_command=True` so callback fires correctly; included welcome emoji in panel title.

### [Prompt 13] Add job description validation
- Added `validate_job_description()` in `chains/analyzer.py` with length, signal-keyword, URL, and single-line checks.
- Wired validation into `main.py` `analyze` and `apply` commands after JD collection.
- Prints yellow warning and prompts user to continue anyway if validation fails.
- **Improvement beyond spec:** Extracted reusable `_maybe_validate_jd()` helper so both commands share the same UX; default answer is `False` for safety.

### [Prompt 14] Add --dry-run flag to apply command
- Added `--dry-run` boolean option to `apply` command (default False).
- When enabled, runs JD validation + analyzer, displays full results, then exits cleanly.
- Skips tailorer, cover letter generator, file saves, and tracker update.
- **Improvement beyond spec:** Printed dry-run completion inside a styled Rich Panel for consistency.

### [Prompt 15] Refactor prompt templates to separate files
- Created `prompts/` directory with 8 plain-text template files.
- Extracted all hardcoded prompts from `analyzer`, `tailorer`, `cover_letter`, and `followup` chains.
- Added `_load_prompt()` helper in each chain file to read templates from disk.
- **Improvement beyond spec:** Prompts can now be edited without touching Python code, making A/B testing and iteration easier.

### [Prompt 16] Centralize error handling
- Added `handle_error()` in `utils/helpers.py` with red ✗ prefix and optional dim hint.
- Wrapped resume parsing in `main.py` with `FileNotFoundError` and `ValueError` handlers.
- Wrapped all LLM chain calls with `ConnectionError` → "Cannot reach Ollama" and general `Exception` handlers.
- Replaced bare `Exception` catches in file saves with `OSError` and `handle_error`.
- **Improvement beyond spec:** No raw Python tracebacks shown to users during normal operation; all errors are friendly Rich-formatted messages.

### [Prompt 17] Add type hints, docstrings, and parser error handling
- Verified complete type hints across `utils/resume_parser.py`, `utils/tracker.py`, and all `chains/` files.
- Added `OutputParserException` handling in `chains/analyzer.py` with clear `ValueError` message.
- Confirmed all string formatting uses f-strings consistently; no unused imports remain.

### [Prompt 18] Add config validation
- Added `validate_config()` in `config.py` with Rich warnings for missing model, unreachable Ollama, and missing resume.
- Used `socket.connect_ex` with short timeout to test localhost Ollama port without blocking.
- Called `validate_config()` from `@app.callback()` in `main.py` so warnings appear once at startup.
- **Improvement beyond spec:** Passed existing `console` instance to avoid creating a second Rich console.

### [Prompt 19] Improve tracker robustness and add status command
- Validated non-empty company/role in `add_application()`; raise `ValueError` if empty.
- Handled empty rows in `show_tracker()`; print "No applications found." when all rows are blank.
- Gracefully skipped corrupt date formats in `get_followups_due()` instead of crashing.
- Added `update_status()` in `utils/tracker.py` with validated status enum.
- Exposed `status` as new CLI command with `--company`, `--role`, `--status` options.
