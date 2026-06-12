# Best Practices & Testing — Long Horizon Prompt

## Mission

You are improving the Job Search CLI Tool (`job_search_tool`) by implementing every item from two implementation plans. Start by reading both documents to understand the full scope:

- [docs/implementation_plans/best_practices_plan.md](../implementation_plans/best_practices_plan.md)
- [docs/implementation_plans/testing_plan.md](../implementation_plans/testing_plan.md)

Execute every item in the **Prioritized Fix List** (best practices) and the **Prioritized Test List** (testing), in order. Mark each phase as completed in the respective plan file after it has been implemented.

---

## Git Setup (do this first)

1. If a branch named `feature/job-search-best-practices` does not exist, create it from `main` and check it out.
2. After completing each numbered step, stage all new and modified files, commit, and push.
3. Use this commit message format: `[Prompt N] Short description of what was implemented`

---

## Environment Assumptions

- Python 3.11+
- Ollama running locally at http://localhost:11434 with `llama3.1` already pulled, OR Ollama Cloud Pro accessible via `OLLAMA_BASE_URL`
- Repo root is the working directory
- The project lives under `job_search_tool/`
- Prompts 1–38 are already complete and working on `main`

---

## Execution Order

Run these sequentially. Each produces working, committed code.

### Phase A: Best Practices Fixes

| # | Name | Description | Severity | Complexity |
|---|------|-------------|----------|------------|
| 1 | Wrap `wb.save()` in tracker for `PermissionError` | In `utils/tracker.py`, wrap all `wb.save(path)` calls (lines 149, 287, 339, 388) in try/except. Catch `PermissionError` and re-raise as a user-friendly exception with the message: "Tracker file may be open in another program. Close it and try again." | Major | Low |
| 2 | Use `st.session_state` for analysis results | In `app.py`, store `analysis`, `tailored_resume`, and `cover_letter` in `st.session_state` so they persist across Streamlit reruns. Ensure results are not recomputed or lost when the user interacts with other widgets. | Major | Medium |
| 3 | Add `st.session_state` gating for apply pipeline | In `app.py`, gate the Full Application mode pipeline so it only reruns when inputs change. Clear `session_state` outputs when the job description text changes. | Medium | Medium |
| 4 | Add Windows reserved name check to `make_slug` | In `utils/helpers.py:28`, extend `make_slug` to reject Windows reserved names (CON, PRN, AUX, NUL, COM1–COM9, LPT1–LPT9) and strip trailing dots/spaces. | Minor | Low |
| 5 | Validate `--file` path is actually a file | In `main.py`, add a check in `get_job_description` (or the `--file` option handler) that the resolved path `is_file()`. If not, raise a `typer.BadParameter` with a clear message. | Minor | Low |
| 6 | Add docstring to `first_run_check` | In `main.py:72`, add a docstring to the Typer callback explaining it runs before every subcommand to check for missing resume / `.env`. | Minor | Low |
| 7 | Document unwrapped `ConnectionError` in chains | Add a note to the module-level docstrings in `chains/analyzer.py`, `chains/tailorer.py`, `chains/cover_letter.py`, and `chains/followup.py` stating that `.invoke()` calls are not wrapped and callers must handle connection errors. | Minor | Low |

### Phase B: Test Suite

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 8 | Create test structure and `conftest.py` | Create `tests/` directory with `conftest.py` containing the fixtures: `sample_resume_text`, `sample_job_description`, `sample_job_analysis`, `tmp_tracker`, and `mock_llm` (see testing plan for exact definitions). | Low |
| 9 | Test `utils/resume_parser.py` | Create `tests/test_resume_parser.py` with tests for: multi-page text PDF, missing file, empty PDF, image-based page warning, and preview length cap. Mock `pdfplumber` where needed. | Medium |
| 10 | Test `utils/tracker.py` | Create `tests/test_tracker.py` with tests for: `add_application` (date logic + empty validation), `application_exists` (case-insensitive + missing file), `delete_application`, `edit_application` (editable vs non-editable fields), `update_status` (valid/invalid status), `get_followups_due`, and `show_tracker` on empty tracker. Use `tmp_path` fixture. | Medium |
| 11 | Test `chains/analyzer.py` | Create `tests/test_analyzer.py` with tests for: `validate_job_description` (realistic, short, URL-only, missing keywords) and `analyze_job` with `FakeListChatModel` (valid JSON + malformed JSON). | Medium |
| 12 | Test remaining chains | Create `tests/test_tailorer.py`, `tests/test_cover_letter.py`, and `tests/test_followup.py`. Each should have at least one happy-path test using the `mock_llm` fixture to verify prompt variable population and string return. | Low |
| 13 | Test `config.py` | Create `tests/test_config.py` with tests for: `validate_config` prints no warnings when valid, and warns when resume is missing. Mock `os.getenv` and socket checks as needed. | Low |
| 14 | Test CLI (`main.py`) | Create `tests/test_cli.py` with Typer `CliRunner` integration tests for: `verify` exits 1 when resume missing, `verify` exits 0 when valid, `analyze` with `--file` and valid input, `tracker --show` on empty tracker, and `tracker --delete` with confirmation input. | Medium |
| 15 | Add CI workflow | Create `.github/workflows/test.yml` as specified in the testing plan. Mark any tests requiring real Ollama with `@pytest.mark.ollama` and exclude them from CI. | Low |

---

## Optional / Nice-to-Have

These items from the plans are **not required** but may be tackled if time permits:

- **Shared console singleton** — A single `utils/console.py` with a singleton `Console()` to replace scattered console instances across `utils/tracker.py`, `utils/resume_parser.py`, and `config.py`. Complexity: Low.
- **Coverage reporting** — Add `pytest-cov` to CI and set a minimum coverage threshold (e.g., 60% project-wide). Complexity: Low.

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
- A plain-English summary of what was implemented
- Any improvements made beyond the spec (better error messages, type hints, docstrings, edge cases)
- Any deviations from the spec and why

---

## Refactoring and Improvements

As you implement, use your judgment to add sensible improvements beyond what the spec explicitly describes. Good candidates include: better error messages, type hints, docstrings, input validation, DRY abstractions, defensive handling of edge cases, or small UX improvements in CLI/Streamlit output. You do not need to ask permission for these — just do them and note them in CHANGELOG.md under the relevant entry.

---

## Rules

- Complete, commit, and push to remote each step before starting the next.
- If a step produces errors, fix them before moving on. Do not proceed on broken code.
- Do not batch multiple steps into one commit.
- Always commit CURRENT_TASK.md and CHANGELOG.md alongside the step's code files.
- All markdown files are located in the `docs/` folder.
- Preserve all existing CLI behavior, Streamlit UI behavior, and tracker file formats.
- Run a quick smoke test (`python -m main --help`, `streamlit run app.py --help`, `pytest tests/ -x`) after each commit to verify nothing is broken.

---

## When All Steps Are Complete

- Update CURRENT_TASK.md to reflect that the build is finished.
- Confirm all commits are on the branch with correct messages.
- List any files not committed.
- Print a summary of what was implemented, all improvements made beyond the spec, and any deviations.
- Push the branch to remote.
- Do not open a pull request.
