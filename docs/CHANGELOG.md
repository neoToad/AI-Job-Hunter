# Changelog

## Build: Job Search Tool Follow-up Prompts (11–20)

Branch: `feature/job-search-followup`

---

### [Prompt 11] Fix output directory and init files
- Ensured `chains/__init__.py` and `utils/__init__.py` already exist (no changes needed).
- Updated `config.py` to create `data/` and `resume/` directories on import alongside existing output dirs.
- Wrapped output file save steps in `main.py` with `OSError`-specific try/except and a Rich-formatted hint.
- **Improvement beyond spec:** Used `OSError` instead of bare `Exception` for more precise error handling; added a hint about checking directory writability.
