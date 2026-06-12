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

## [Prompt 36] Standardize load_workbook read-only usage

- Added a module-level comment documenting the openpyxl pattern: `read_only=True` for pure reads, `read_only=False` for mutations.
- `application_exists`, `show_tracker`, and `get_followups_due` already used `read_only=True` — no changes needed.
- Explicitly added `read_only=False` to `load_workbook` calls in `_get_or_create_workbook`, `update_status`, `delete_application`, and `edit_application` to document intent.
- No functional changes — `read_only=False` is the openpyxl default; the explicit flag serves as a safety signal for future maintainers.

## [Prompt 37] Extract shared run_apply_pipeline

- Created `pipelines.py` with a shared `run_apply_pipeline()` function and `PipelineStep` enum + `PipelineResult` dataclass.
- The pipeline encapsulates: analysis (optional reuse), tailoring + cover-letter generation, file writes, and tracker update.
- Supports an optional `on_step` callback so the Streamlit UI can update its progress bar (`ANALYZING` → `TAILORING` → `SAVING` → `DONE`).
- Refactored `main.py:apply()` to call `run_apply_pipeline()` after gathering inputs, running analysis, and collecting source/notes from the user.
- Removed `_run_tailoring_and_cover_letter()` and `_save_outputs()` from `main.py` since their logic now lives in the shared pipeline.
- Refactored `app.py:Full Application` mode to call `run_apply_pipeline()` with a step callback that maps each `PipelineStep` to a `st.progress()` percentage.
- Removed now-unused `asyncio`, `make_slug`, and `add_application` imports from `app.py`.

## [Prompt 38] Shared analysis display formatter

- Added `JobAnalysis.to_display_dict() -> dict[str, list[str]]` in `chains/analyzer.py` that returns a structured dict of list-based sections.
- Added `_SECTION_STYLES` mapping and `_render_bullet_table(title, items, icon)` helper in `main.py` to eliminate repetitive Rich table-building logic.
- Refactored `main.py:_display_analysis()` to iterate over `result.to_display_dict()` instead of 5 separate `if result.x:` blocks.
- Refactored `app.py:analyze mode` to iterate over `result.to_display_dict()` with a `_SECTION_TITLES` mapping, replacing 5 separate `if result.x:` blocks.
- Both CLI and Streamlit now render from the same structured data source, with each UI layer handling its own presentation (Rich tables vs Streamlit expanders).

## [Final] Shared console singleton + shared resume parsing helper

- Created `utils/console.py` with a module-level singleton `console = Console()`.
- Updated `utils/tracker.py` to import `console` from `utils.console` instead of creating a local `Console()`.
- Updated `utils/resume_parser.py` to import `console` from `utils.console` instead of creating `_console = Console()`.
- Updated `config.py:validate_config()` to fall back to the shared `console` instead of creating a fresh `Console()` inline.
- **Shared resume parsing:** Removed redundant `config.RESUME_PATH.exists()` pre-checks from `main.py:analyze()`, `main.py:_gather_inputs()`, and `app.py:_cached_resume_text()`.
  - `get_resume_text()` (in `utils/resume_parser.py`) already raises uniform `FileNotFoundError` / `ValueError` when the file is missing or unparseable.
  - Both CLI and Streamlit callers now rely on the same underlying exceptions, handling them in their UI-appropriate way (`handle_error()` vs `st.error()`).

## [Step 1] Wrap `wb.save()` in tracker for PermissionError

- Added `_safe_save(wb, path)` helper in `utils/tracker.py` that catches `PermissionError` from `wb.save()` and re-raises it with a user-friendly message: "Tracker file may be open in another program. Close it and try again."
- Replaced all four raw `wb.save(path)` calls in `add_application`, `update_status`, `delete_application`, and `edit_application` with calls to `_safe_save`.
- **Improvement:** Centralized the save logic so future enhancements (e.g., backup-on-save, retry logic) only require changing one place.

## [Step 2] Use `st.session_state` for analysis results

- Added `key="cover_letter"` and `key="tailored_resume"` to the editable `st.text_area` widgets in `app.py` Full Application mode.
- Removed the explicit `value=` parameter from these text areas; Streamlit now reads the initial value from `st.session_state` (set by the pipeline) and writes user edits back to the same key automatically.
- **Improvement:** User edits to the generated cover letter or tailored resume are now preserved across Streamlit reruns instead of being reset when the user interacts with other widgets.

## [Step 3] Add `st.session_state` gating for apply pipeline

- Updated `_clear_stale_state` in `app.py` to accept `current_mode` and clear cached results when either the job description or the selected mode changes.
- Added `"analysis"` to the list of keys cleared on input change (previously only `"analyze_result"` was cleared, which left Full Application mode's `analysis` state stale).
- Extended `_clear_stale_state` calls to both Analyze Job and Full Application modes so stale results are consistently cleared when the user switches modes or edits the job description.
- **Improvement:** Prevents stale analysis data from one mode appearing in the other mode after a mode switch.

## [Step 4] Add Windows reserved name check to `make_slug`

- `sanitize_filename` in `utils/helpers.py` already rejected Windows reserved names (CON, PRN, AUX, NUL, COM1–9, LPT1–9) and stripped trailing dots/spaces.
- **Fix:** Added a second `.strip(" ._-")` after truncation, because slicing to `max_length` can reintroduce trailing dots or spaces if the original string contained them near the boundary.
- Re-checked reserved names after the post-truncation strip to ensure the final filename is safe.

## [Step 5] Validate `--file` path is actually a file

- In `main.py:get_job_description`, the `--file` validation already checked `file.is_file()`, but it used `handle_error()` which exits with code 1.
- **Change:** Replaced the `handle_error()` call with `raise typer.BadParameter(...)` so Typer presents the error as a clean parameter-validation message (exit code 2) consistent with other CLI tools.

## [Step 6] Add docstring to `first_run_check`

- Expanded the docstring on `first_run_check` in `main.py` to clarify that Typer invokes it automatically before every subcommand, that it checks for missing resume / `.env`, and that missing files are non-blocking so the user still sees the exact error from the target command.

## [Step 7] Document unwrapped `ConnectionError` in chains

- Added a module-level `.. note::` to `chains/analyzer.py`, `chains/tailorer.py`, `chains/cover_letter.py`, and `chains/followup.py`.
- Each note states that the inner `.invoke()` call is not wrapped in try/except and that callers must handle `ConnectionError` and other LLM exceptions.
- **Improvement:** Makes the intentional lack of error wrapping explicit to future maintainers and consumers of the chain API.

## [Step 8] Create test structure and `conftest.py`

- Created `tests/` directory at the repo root.
- Added `tests/conftest.py` with five shared fixtures per the testing plan:
  - `sample_resume_text`, `sample_job_description`, `sample_job_analysis`
  - `tmp_tracker` (pre-seeded with one row)
  - `mock_llm` (monkey-patches `chains.llm.get_llm` with `FakeListChatModel`)
- Added `pyproject.toml` with `[tool.pytest.ini_options]`:
  - `pythonpath = ["job_search_tool"]` so test imports mirror the app's import style.
  - `testpaths = ["tests"]` and `markers = ["ollama"]` for CI filtering.

## [Step 9] Test `utils/resume_parser.py`

- Created `tests/test_resume_parser.py` with five unit tests:
  1. `test_parse_resume_multi_page` — mocks `pdfplumber.open` with two pages, verifies double-newline joining.
  2. `test_parse_resume_file_not_found` — asserts `FileNotFoundError` for a non-existent path.
  3. `test_parse_resume_empty_pdf` — mocks an empty page and asserts `ValueError`.
  4. `test_parse_resume_image_page_warning` — mocks a mixed PDF (empty page + text page), asserts warning via `console.print` mock, and verifies extraction continues.
  5. `test_preview_resume_length_cap` — mocks a 1000-char page and asserts `preview_resume(..., chars=50)` returns exactly 50 characters.

## [Step 10] Test `utils/tracker.py`

- Created `tests/test_tracker.py` with 14 unit tests covering all public tracker functions:
  - `add_application` — date logic (+14 days follow-up), empty/whitespace validation
  - `application_exists` — case-insensitive match, missing file returns False
  - `delete_application` — removes correct row, returns False when not found
  - `edit_application` — updates editable field, rejects non-editable field
  - `update_status` — changes status, raises `ValueError` for invalid status
  - `get_followups_due` — filters to Applied rows with follow-up date ≤ today
  - `show_tracker` — prints empty-tracker message without crashing
- **Fix:** `utils/tracker.py:show_tracker` was iterating all rows including the header row, causing an empty tracker (headers only) to render a table instead of the "No applications found" message. Added `min_row=2` to `iter_rows` to skip the header.

## [Step 11] Test `chains/analyzer.py`

- Created `tests/test_analyzer.py` with six tests:
  - Four tests for `validate_job_description` covering realistic input, short input, URL-only input, and missing-keyword input.
  - Two tests for `analyze_job` using `FakeListChatModel`: one with valid JSON (asserts `JobAnalysis` fields), one with malformed JSON (asserts `ValueError`).
- **Fix:** Updated `tests/conftest.py:mock_llm` to monkeypatch `get_llm` inside every chain module that imports it directly (`chains.analyzer`, `chains.tailorer`, `chains.cover_letter`, `chains.followup`). Python binds `from chains.llm import get_llm` at import time, so patching `chains.llm.get_llm` alone leaves stale references in the consumer modules.


