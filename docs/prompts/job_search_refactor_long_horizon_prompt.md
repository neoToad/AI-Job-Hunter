# Refactor Prompts 31–38 — Long Horizon Prompt

## Mission

You are refactoring the Job Search CLI Tool (`job_search_tool`). Start by reading the implementation spec document that defines exactly what to refactor:

- [docs/implementation_plans/refactor_plan.md](../implementation_plans/refactor_plan.md)

The plan is your implementation spec — execute every item in the **Prioritized Refactor List**, in order. Mark each phase as completed in the file after it has been completed.

---

## Git Setup (do this first)

1. If a branch named `feature/job-search-refactor` does not exist, create it from `main` and check it out.
2. After completing each numbered step in the prompt plan (31, 32, 33, etc.), stage all new and modified files, commit, and push.
3. Use this commit message format: `[Prompt N] Short description of what was refactored`

---

## Environment Assumptions

- Python 3.11+
- Ollama running locally at http://localhost:11434 with `llama3.1` already pulled, OR Ollama Cloud Pro accessible via `OLLAMA_BASE_URL`
- Repo root is the working directory
- The project lives under `job_search_tool/`
- Prompts 1–30 are already complete and working on `main` or `feature/job-search-round-3`

---

## Execution Order

Run these sequentially. Each produces working, committed code.

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 31 | Extract `_load_prompt` to shared helper | Move the identical 3-line `_load_prompt()` from `chains/analyzer.py`, `chains/tailorer.py`, `chains/cover_letter.py`, and `chains/followup.py` into a new `chains/utils.py` as `load_prompt(name: str) -> str`. Update all imports. | Low |
| 32 | Extract resume parse + error handling in CLI | In `main.py`, create `_parse_resume_for_cli() -> str` that wraps `parse_resume(config.RESUME_PATH)` with the `console.status("Parsing resume...")` spinner and identical `FileNotFoundError` / `ValueError` handling. Replace the duplicated blocks in `analyze()` and `apply()`. | Low |
| 33 | Extract `_run_chain_with_spinner` and standardize error handling | In `main.py`, create `_run_chain_with_spinner(description: str, fn: Callable[[], T]) -> T` that wraps the `Progress(SpinnerColumn(), TextColumn(...))` context and generic exception handling. Replace all ~6 duplicated Progress blocks. Also standardize on `handle_error()` for fatal errors and `console.print(...) + raise typer.Exit(0)` for user aborts. | Low |
| 34 | Break `apply()` into sub-functions | Refactor `main.py:apply()` (~170 lines) into private helpers: `_gather_inputs()`, `_run_analysis()`, `_run_tailoring_and_cover_letter()`, and `_save_outputs()`. Preserve all existing behavior, user prompts, and tracker updates. | Medium |
| 35 | Extract tracker delete/edit helpers | In `main.py`, extract `_tracker_delete(company, role)` and `_tracker_edit(company, role, field, value)` from the `tracker()` command. Keep the single Typer command entry point but delegate to helpers. | Low |
| 36 | Standardize `load_workbook` read-only usage | In `utils/tracker.py`, ensure `read_only=True` is used for pure reads (`application_exists`) and explicitly open read-write for mutations (`add_application`, `update_status`, `delete_application`, `edit_application`). Document the pattern with a brief comment. | Low |
| 37 | Extract shared `run_apply_pipeline` | Create a new `pipelines.py` module with a pure function `run_apply_pipeline(resume, job_description, source, skip_tailor, dry_run)` that returns a dataclass with `analysis`, `tailored_resume`, `cover_letter`, and `saved_paths`. Both `main.py:apply()` and `app.py:Full Application mode` should call this. The UI gets progress via a simple step enum or generator. | High |
| 38 | Shared analysis display formatter | Add a `JobAnalysis.to_display_dict()` method or a small formatter that returns a structured dict of sections (must_have, matching_skills, missing_skills, red_flags, nice_to_have). Update both `main.py:_display_analysis()` and `app.py:analyze mode` to render from it. | Medium |

---

## Optional / Nice-to-Have

These items from the refactor plan are **not required** but may be tackled if time permits:

- **Shared console singleton** — A single `utils/console.py` with a singleton `Console()` to replace scattered console instances across `utils/tracker.py`, `utils/resume_parser.py`, and `config.py`. Complexity: Low.
- **`_render_bullet_table` helper** — Extract repetitive table-building logic from `_display_analysis()` into `_render_bullet_table(title, items, icon)`. Complexity: Low.

---

## Tracking Files

Maintain two markdown files in `docs/` throughout the entire build. Update them continuously — not just at the end.

### docs/CURRENT_TASK.md
Keep this file up to date at all times. It should always reflect exactly what is happening right now and should be updated before working on the step:
- The current step number and name
- What you are actively working on
- Any blockers or decisions being made
- What the next step will be

Overwrite it completely each time you move to a new step. It should never describe a completed step — only the live current state.

### docs/CHANGELOG.md
Append an entry after every commit. Each entry should include:
- The step number and commit message
- A plain-English summary of what was refactored
- Any improvements made beyond the spec (better error messages, type hints, docstrings, edge cases)
- Any deviations from the spec and why

---

## Refactoring and Improvements

As you refactor, use your judgment to add sensible improvements beyond what the spec explicitly describes. Good candidates include: better error messages, type hints, docstrings, input validation, DRY abstractions, defensive handling of edge cases, or small UX improvements in CLI/Streamlit output. You do not need to ask permission for these — just do them and note them in CHANGELOG.md under the relevant entry.

---

## Rules

- Complete, commit, and push to remote each step before starting the next.
- If a step produces errors, fix them before moving on. Do not proceed on broken code.
- Do not batch multiple steps into one commit.
- Always commit CURRENT_TASK.md and CHANGELOG.md alongside the step's code files.
- All markdown files are located in the `docs/` folder.
- Preserve all existing CLI behavior, Streamlit UI behavior, and tracker file formats.
- Run a quick smoke test (`python -m main --help`, `streamlit run app.py --help`) after each commit to verify imports are not broken.

---

## When All Steps Are Complete

- Update CURRENT_TASK.md to reflect that the build is finished.
- Confirm all commits are on the branch with correct messages.
- List any files not committed.
- Print a summary of what was refactored, all improvements made beyond the spec, and any deviations.
- Push the branch to remote.
- Do not open a pull request.
