# Output Formats (PDF Resume & DOCX Cover Letter) — Long Horizon Prompt

## Mission

You are extending the Job Search CLI Tool (`job_search_tool`) to replace its plain-text `.txt` outputs with professionally formatted files: a `.pdf` tailored resume and an editable `.docx` cover letter. Start by reading both implementation plans to understand the full scope:

- [docs/implementation_plans/resume_pdf_output_plan.md](../implementation_plans/resume_pdf_output_plan.md)
- [docs/implementation_plans/cover_letter_docx_output_plan.md](../implementation_plans/cover_letter_docx_output_plan.md)

Execute every item in the **Acceptance Criteria** of both plans, in order. Mark each phase as completed in the respective plan file after it has been implemented.

---

## Git Setup (do this first)

1. If a branch named `feature/job-search-output-formats` does not exist, create it from `main` and check it out.
2. After completing each numbered step, stage all new and modified files, commit, and push.
3. Use this commit message format: `[Prompt N] Short description of what was implemented`

---

## Environment Assumptions

- Python 3.11+
- Ollama running locally at http://localhost:11434 with `llama3.1` already pulled, OR Ollama Cloud Pro accessible via `OLLAMA_BASE_URL`
- Repo root is the working directory
- The project lives under `job_search_tool/`
- Prior feature branches are already complete and working on `main`

---

## Execution Order

Run these sequentially. Each produces working, committed code.

### Phase A: Shared Renderer Foundation

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 1 | Create `utils/renderers.py` | Create the shared renderer module with `render_resume_pdf(structured_resume: dict, path: Path) -> None` and `render_cover_letter_docx(text: str, path: Path) -> None`. Add graceful fallback to `.txt` for each if the required binary/library is missing. | Medium |
| 2 | Create `templates/resume.html` | Jinja2 template with standard resume layout (contact header, experience blocks, skills, education). Use CSS for fonts, spacing, and page breaks. Keep it single-column to start. | Medium |
| 3 | Update `requirements.txt` | Add `Jinja2`, `pdfkit`, and `python-docx==1.1.2`. Document the non-Pip `wkhtmltopdf` binary prerequisite in a comment. | Low |

### Phase B: Tailored Resume → PDF

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 4 | Define `TailoredResume` Pydantic models | In `chains/tailorer.py`, add `ExperienceEntry` and `TailoredResume` models (contact, summary, experience[], education[], skills[]). | Low |
| 5 | Update `tailorer_system.txt` prompt | Instruct the LLM to return valid JSON with keys: contact, summary, experience, education, skills. Forbid Markdown and plain text. | Low |
| 6 | Refactor `tailor_resume` chain | Return a structured dict via `JsonOutputParser`. Catch `OutputParserException` and raise `ValueError` with a friendly retry message, identical to `analyzer.py`. | Medium |
| 7 | Wire PDF rendering into pipeline | In `pipelines.py`, replace `write_text()` for the resume with `render_resume_pdf(tailored_resume_dict, resume_out)` where `resume_out` ends in `.pdf`. | Low |
| 8 | Update CLI output labels | In `main.py`, update the `apply()` summary panel to reference `.pdf` instead of `.txt`. | Low |
| 9 | Update Streamlit resume UI | In `app.py`, remove or re-label the editable "Tailored Resume" text area. Replace with a download button for the `.pdf` (or keep a read-only preview). | Medium |

### Phase C: Cover Letter → DOCX

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 10 | Wire DOCX rendering into pipeline | In `pipelines.py`, replace `write_text()` for the cover letter with `render_cover_letter_docx(cover_letter, cl_out)` where `cl_out` ends in `.docx`. | Low |
| 11 | Update CLI output labels | In `main.py`, update the `apply()` summary panel to reference `.docx` instead of `.txt`. | Low |
| 12 | Update Streamlit cover letter UI | In `app.py`, change the editable "Cover Letter" text area to a download button for the `.docx`, or keep the text area as a preview with a download link below it. | Medium |
| 13 | Prune tracker cover-letter column | In `utils/tracker.py`, remove `"Cover Letter Path"` from `_HEADERS` and drop the `cover_letter_path` parameter from `add_application()`. Verify old trackers with the orphaned column still render in `show_tracker`. | Medium |

### Phase D: Testing & Fallbacks

| # | Name | Description | Complexity |
|---|------|-------------|------------|
| 14 | Unit test `render_resume_pdf` | Mock `pdfkit.from_string`; assert output file exists and has `.pdf` extension when passed a dummy dict. | Low |
| 15 | Unit test `render_cover_letter_docx` | Assert output file exists, has `.docx` extension, and contains expected paragraph text. | Low |
| 16 | Unit test `tailor_resume` with JSON output | Use `FakeListChatModel` returning valid JSON; assert returned dict has expected keys. | Low |
| 17 | Update tracker tests | Remove `cover_letter_path` assertions from `add_application` and `show_tracker` tests. Add a test for an old tracker that still contains the orphaned `"Cover Letter Path"` column. | Low |
| 18 | Integration smoke tests | Run `apply --dry-run` and assert no `.txt` resume or cover-letter files are written in `output/`. | Medium |
| 19 | CI compatibility | Update `.github/workflows/test.yml` to install `wkhtmltopdf` or skip PDF rendering tests when the binary is absent. | Low |

---

## Optional / Nice-to-Have

These items from the plans are **not required** but may be tackled if time permits:

- **Date block in cover letter** — Auto-prepend today's date as a formatted paragraph before the salutation in `render_cover_letter_docx`. Complexity: Low.
- **Multiple resume templates** — Offer a `--template` CLI option to choose between single-column and two-column resume layouts. Complexity: Medium.
- **Markdown stripping in DOCX** — Strip simple Markdown syntax (`**bold**`, `_italic_`) from cover letter text before writing to `.docx`, or update the prompt to forbid Markdown. Complexity: Low.

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
- Preserve all existing CLI behavior, Streamlit UI behavior, and tracker file formats (except the intentionally removed cover-letter column).
- Run a quick smoke test (`python -m main --help`, `streamlit run app.py --help`, `pytest tests/ -x`) after each commit to verify nothing is broken.

---

## When All Steps Are Complete

- Update CURRENT_TASK.md to reflect that the build is finished.
- Confirm all commits are on the branch with correct messages.
- List any files not committed.
- Print a summary of what was implemented, all improvements made beyond the spec, and any deviations.
- Push the branch to remote.
- Do not open a pull request.
