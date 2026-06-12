# Current Task

## Build Complete — Prompts 31–38 Finished

**Status:** All 8 prompts are complete and committed to `feature/job-search-refactor`.

**Summary of what was refactored:**
- Prompt 31: Extracted `_load_prompt` to shared `chains/utils.py` helper; removed duplication across 4 chain modules.
- Prompt 32: Extracted `_parse_resume_for_cli()` in `main.py` to DRY resume parsing + error handling.
- Prompt 33: Extracted `_run_chain_with_spinner()` in `main.py` replacing 5 duplicated Progress blocks; standardized fatal errors to `handle_error()`.
- Prompt 34: Broke `apply()` into `_gather_inputs()`, `_run_analysis()`, `_run_tailoring_and_cover_letter()`, and `_save_outputs()`.
- Prompt 35: Extracted `_tracker_delete()` and `_tracker_edit()` from the `tracker()` command.
- Prompt 36: Standardized `load_workbook` usage with explicit `read_only=True` for reads and `read_only=False` for mutations.
- Prompt 37: Created `pipelines.py` with `run_apply_pipeline()`, `PipelineStep`, and `PipelineResult`; refactored both `main.py:apply()` and `app.py:Full Application` to use it.
- Prompt 38: Added `JobAnalysis.to_display_dict()` and refactored both CLI and Streamlit analysis display to render from it.

**Improvements beyond the spec:**
- Moved `analyze_job` and `validate_job_description` imports to module level in `main.py`, fixing a latent bug where `_maybe_validate_jd` relied on side-effect inline imports.
- Added `_render_bullet_table()` helper in `main.py` for cleaner Rich table construction.
- Added `notes` parameter to `run_apply_pipeline()` so both CLI and Streamlit can pass notes to the tracker.
- Added docstrings and type hints to all new helpers and the pipeline module.

**Deviations:** None.

**Branch:** `feature/job-search-refactor` (pushed to remote).
