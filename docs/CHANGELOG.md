# Changelog

## [Unreleased]

Branch: `main`

---

<!-- New entries go below this line -->

## [Prompt 31] Extract _load_prompt to shared helper in chains/utils.py

- Created `chains/utils.py` with a shared `load_prompt(name: str) -> str` helper that loads prompt templates from the `prompts/` directory.
- Removed duplicated `_load_prompt()` functions from `chains/analyzer.py`, `chains/tailorer.py`, `chains/cover_letter.py`, and `chains/followup.py`.
- Updated all four modules to import `load_prompt` from `chains.utils`.
- Also removed now-unused `from pathlib import Path` imports in the refactored chain modules.

## [Prompt 32] Extract resume parse + error handling in CLI

- Added `_parse_resume_for_cli() -> str` in `main.py` that wraps `get_resume_text(config.RESUME_PATH)` with the Rich spinner and uniform `FileNotFoundError` / `ValueError` handling via `handle_error()`.
- Replaced the duplicated ~12-line resume-parsing blocks in `analyze()` and `apply()` with a single call to `_parse_resume_for_cli()`.
- No functional changes — purely DRY cleanup with a small UX improvement (the same error messages and hints are preserved exactly).

## [Prompt 33] Extract _run_chain_with_spinner and standardize error handling

- Added `_run_chain_with_spinner(description, fn, step_name)` in `main.py` that wraps the `Progress(SpinnerColumn(), TextColumn(...))` context and generic `ConnectionError` / `Exception` handling.
- Replaced 5 duplicated Progress blocks across `analyze()`, `apply()`, and `followup()` with calls to `_run_chain_with_spinner()`.
- Extracted the inline async `_tailor_and_cover()` from `apply()` into a named nested function so it can be passed cleanly to the spinner helper.
- **Standardized error handling:** Converted all fatal-error exits from `console.print("[bold red]...")` + `raise typer.Exit(1)` to `handle_error()` calls. This includes:
  - `verify()`: missing resume
  - `analyze()` / `apply()`: missing resume before parsing
  - `followup()`: invalid selection
  - `tracker()`: missing entry on delete or edit
- User aborts (`--dry-run`, confirmation declines, empty input) continue to use `console.print(...)` + `raise typer.Exit(0)` as required by the spec.

## [Prompt 34] Break apply() into sub-functions

- Refactored `apply()` (~170 lines → ~40 lines) into four private helpers:
  - `_gather_inputs(file, url)` — validates resume exists, parses it, resolves job description, and runs JD validation.
  - `_run_analysis(resume_text, job_description)` — runs the analyzer chain via `_run_chain_with_spinner` and displays results.
  - `_run_tailoring_and_cover_letter(analysis, resume_text, job_description, skip_tailor)` — handles both skip-tailor and concurrent tailor+CL paths.
  - `_save_outputs(tailored_resume, cover_letter, analysis)` — writes files, prompts for source/notes, updates tracker, and prints the summary panel.
- Moved `analyze_job` and `validate_job_description` imports to module level to fix a latent bug where `_maybe_validate_jd` relied on side-effect inline imports in callers.
- Removed redundant inline imports from `analyze()`, `_gather_inputs`, and `_run_analysis`.
- All user prompts, tracker updates, and duplicate checks are preserved exactly.

## [Prompt 35] Extract tracker delete/edit helpers

- Extracted `_tracker_delete(company, role)` and `_tracker_edit(company, role, field, value)` from the `tracker()` Typer command.
- Each helper contains its own validation, confirmation prompt, and tracker call — keeping the command entry point clean.
- `tracker()` now delegates directly: `if delete: _tracker_delete(...); if edit: _tracker_edit(...)`.
- No functional changes.





