# Job Search CLI Tool — Long Horizon Prompt (Prompts 21–30)

## Mission

You are hardening and extending the Job Search CLI Tool (`job_search_tool`). Start by reading the implementation spec documents that define exactly what to build:

- [docs/job_search_tool_prompts_21_24.md](../job_search_tool_prompts_21_24.md)
- [docs/job_search_tool_prompts_25_27.md](../job_search_tool_prompts_25_27.md)
- [docs/job_search_tool_prompts_28_30.md](../job_search_tool_prompts_28_30.md)

These three files contain the full prompt plan. Execute **every prompt in it, in order**, from Prompt 21 through Prompt 30.

---

## Git Setup (do this first)

1. If a branch named `feature/job-search-round-3` does not exist, create it from `main` and check it out.
2. After completing each numbered step in the prompt plan (Prompt 21, Prompt 22, Prompt 23, etc.), stage all new and modified files, commit, and push.
3. Use this commit message format: `[Prompt N] Short description of what was built`

---

## Environment Assumptions

- Python 3.11+
- Ollama running locally at http://localhost:11434 with `llama3.1` already pulled, OR Ollama Cloud Pro accessible via `OLLAMA_BASE_URL`
- Repo root is the working directory
- The project lives under `job_search_tool/`
- Prompts 1–20 are already complete and working on `feature/job-search-followup`

---

## Execution Order

### Block A — Features (Prompts 21–24)
Run these sequentially. Each produces working code.

| # | Name | Description |
|---|------|-------------|
| 21 | Explicit Prompt File Contents | Overwrite all 8 `prompts/*.txt` files with the exact content specified in the spec. Verify placeholders match chain invocations. |
| 22 | File & URL Input for CLI | Replace the "paste until END" input with a proper `--file` / `--url` / stdin helper. Add `beautifulsoup4` and `lxml` to `requirements.txt`. |
| 23 | Tracker Delete & Edit | Add `delete_application()` and `edit_application()` in `utils/tracker.py`. Expose as `tracker --delete` and `tracker --edit` subcommands in `main.py`. |
| 24 | Streamlit UI | Create `app.py` with Analyze and Full Application modes. Add `streamlit` to `requirements.txt`. Reuse all existing chain/utils logic — no duplication. |

### Block B — Audits (Prompts 25–27)
These prompts are **plan-only** — do NOT make code changes. Output markdown plans.

| # | Name | Output file |
|---|------|-------------|
| 25 | Refactor Audit | `docs/refactor_plan.md` |
| 26 | Best Practices Audit | `docs/best_practices_plan.md` |
| 27 | Testing Audit | `docs/testing_plan.md` |

### Block C — Polish (Prompts 28–30)
Run these after the audit plans are complete.

| # | Name | Notes |
|---|------|-------|
| 28 | Documentation | Phase 1: scan and write `docs/documentation_plan.md`. Phase 2: implement — update `README.md`, create `docs/user_guide.md`, `docs/prompt_guide.md`, `docs/troubleshooting.md`. |
| 29 | Performance Audit | Phase 1: scan and write `docs/performance_plan.md`. Phase 2: implement all Low/Medium improvements from the plan (resume cache, `@st.cache_resource`, URL cache, parallelization if identified). |
| 30 | Secrets & .gitignore Audit | Implement directly — no plan phase. Update `.gitignore`, scan for hardcoded values, add `sanitize_filename()`, add URL fetch safety, scrub resume content from errors. |

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
- A plain-English summary of what was built
- Any refactors or improvements made beyond the spec (see below)
- Any deviations from the spec and why

---

## Refactoring and Improvements

As you build, use your judgment to refactor and add sensible improvements beyond what the spec explicitly describes. Good candidates include: better error messages, type hints, docstrings, input validation, DRY abstractions, defensive handling of edge cases, or small UX improvements in CLI/Streamlit output. You do not need to ask permission for these — just do them and note them in CHANGELOG.md under the relevant entry.

---

## Rules

- Complete, commit, and push to remote each step before starting the next.
- If a step produces errors, fix them before moving on. Do not proceed on broken code.
- Do not batch multiple steps into one commit.
- Always commit CURRENT_TASK.md and CHANGELOG.md alongside the step's code files.
- All md files are located in the docs folder.
- For audit prompts (25–27), output the plan markdown file only — do not modify source code.
- For audit implementation prompts (28–29 Phase 2), implement only what the approved plan specifies.

---

## When All Steps Are Complete

- Update CURRENT_TASK.md to reflect that the build is finished.
- Confirm all commits are on the branch with correct messages.
- List any files not committed.
- Print a summary of what was built, all improvements made beyond the spec, and any deviations.
- Push the branch to remote.
- Do not open a pull request.
