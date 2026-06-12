# Changelog

## [v1.3.0] — Best Practices & Testing

### Added
- Wrapped `wb.save()` in tracker for `PermissionError` with user-friendly messaging.
- Used `st.session_state` for analysis results in Streamlit to persist across reruns.
- Added `st.session_state` gating for apply pipeline to clear stale results on input change.
- Added Windows reserved name check to `make_slug` with post-truncation re-validation.
- Validated `--file` path is actually a file using `typer.BadParameter`.
- Added docstring to `first_run_check` explaining Typer callback behavior.
- Documented unwrapped `ConnectionError` in chain module-level docstrings.
- Created test structure and `conftest.py` with shared fixtures (`sample_resume_text`, `sample_job_description`, `sample_job_analysis`, `tmp_tracker`, `mock_llm`).
- Added `pyproject.toml` with pytest configuration (`pythonpath`, `testpaths`, `markers`).
- Unit tests for `utils/resume_parser.py` (multi-page, missing file, empty PDF, image warning, preview cap).
- Unit tests for `utils/tracker.py` (add, exists, delete, edit, update_status, follow-ups, show empty).
- Unit tests for `chains/analyzer.py` (validate JD, analyze with valid/malformed JSON).
- Unit tests for remaining chains (`tailorer`, `cover_letter`, `followup`) happy paths.
- Unit tests for `config.py` (valid config, missing resume warning).
- CLI integration tests (`verify`, `analyze --file`, `tracker --show`, `tracker --delete`).
- GitHub Actions CI workflow running pytest on push/PR, excluding `@pytest.mark.ollama` tests.

### Fixed
- `utils/tracker.py:show_tracker` was iterating all rows including the header, causing empty trackers to render a table instead of the "No applications found" message. Added `min_row=2` to `iter_rows`.
- `tests/conftest.py:mock_llm` patched `get_llm` in every chain module that imports it directly, fixing stale references.

### Changed
- Replaced `handle_error()` with `raise typer.BadParameter(...)` for `--file` path validation.
- Standardized all fatal-error exits to use `handle_error()` calls.
- Refactored `apply()` into four private helpers (`_gather_inputs`, `_run_analysis`, `_run_tailoring_and_cover_letter`, `_save_outputs`).
- Extracted `_tracker_delete` and `_tracker_edit` helpers.
- Extracted shared `_run_chain_with_spinner` and `_parse_resume_for_cli` helpers.
- Standardized `load_workbook` read-only usage with explicit `read_only=False` for mutations.
- Extracted `run_apply_pipeline` into `pipelines.py` with `PipelineStep` enum and `PipelineResult`.
- Shared `console` singleton via `utils/console.py`.
- Shared `_load_prompt` helper in `chains/utils.py`.
- Shared `JobAnalysis.to_display_dict()` formatter used by both CLI and Streamlit.

---

## Previous Releases

- See [CHANGELOG-v1.2.0.md](CHANGELOG-v1.2.0.md)
- See [CHANGELOG-v1.1.0.md](CHANGELOG-v1.1.0.md)
- See [CHANGELOG-v1.0.0.md](CHANGELOG-v1.0.0.md)

