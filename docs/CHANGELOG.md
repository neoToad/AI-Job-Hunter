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


