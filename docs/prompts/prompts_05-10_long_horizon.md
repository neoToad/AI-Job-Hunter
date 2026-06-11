# Long Horizon Prompt: Prompts 5 – 10

> Use this as the master reference when implementing the remaining chain modules, CLI wiring, and documentation. Each numbered section corresponds to the original Prompt N and can be fed individually or in batches.

---

## Context

- Project: `job_search_tool/`
- Already implemented:
  - `config.py` — env-driven constants, Path resolution, output-dir creation on import
  - `chains/llm.py` — `get_llm(temperature=0.3) -> ChatOllama`
  - `utils/resume_parser.py` — `parse_resume(path)` and `preview_resume(path, chars=500)` via pdfplumber
  - `utils/tracker.py` — openpyxl-backed tracker with bold headers, duplicate detection, auto-filled dates, Rich table display, and due-follow-up queries
  - `main.py` — minimal Typer stub with a `verify` command only
- Dependencies installed per `requirements.txt` (langchain, langchain-ollama, pydantic, openpyxl, rich, typer, pdfplumber, python-dotenv, etc.)
- All code must match existing style (PEP 257 docstrings, type hints, `from __future__ import annotations`, pathlib `Path` objects).

---

## Prompt 5 — Job Analysis Chain (`chains/analyzer.py`)

Implement `analyze_job(job_description: str, resume_text: str) -> JobAnalysis`.

### Requirements

1. **Pydantic model `JobAnalysis`** (defined in the same file or a nearby `models.py` if you prefer) with at least these fields:
   - `match_score: int` (0-100)
   - `key_requirements: list[str]`
   - `missing_skills: list[str]`
   - `highlighted_experience: list[str]`
   - `concise_summary: str`
2. Build a LangChain prompt template that takes `{job_description}` and `{resume_text}` and instructs the LLM to return **only** a JSON object conforming to the `JobAnalysis` schema.
3. Use `get_llm()` with structured output (`with_structured_output(JobAnalysis)`) or a JSON-output parser.
4. Handle LLM refusal / malformed JSON gracefully: log a warning and return a fallback `JobAnalysis` with `match_score=0` and a descriptive `concise_summary`.
5. Export `analyze_job` at module level.

### Acceptance criteria

- Unit-like sanity check: `python -c "from chains.analyzer import analyze_job, JobAnalysis; print(JobAnalysis.schema_json())"` prints valid JSON schema.
- AST-validated even if `langchain-ollama` is not installed in the current environment.

---

## Prompt 6 — Resume Tailoring Chain (`chains/tailorer.py`)

Implement `tailor_resume(resume_text: str, job_analysis: JobAnalysis) -> str`.

### Requirements

1. Accept the **original parsed resume text** and the `JobAnalysis` object produced in Prompt 5.
2. Build a LangChain prompt that asks the LLM to rewrite the resume so that:
   - Missing skills gaps are honestly addressed (e.g., "Familiar with X through coursework / personal project" where appropriate) or omitted if no evidence exists.
   - Highlighted experience is brought to the forefront.
   - Keyword alignment with `key_requirements` is improved.
3. The prompt must explicitly instruct the LLM to keep the resume **truthful** — no invented jobs, titles, or degrees.
4. Return the tailored resume text as a plain string.
5. Save the resulting text to `TAILORED_RESUMES_DIR` as a `.md` file with a sanitized filename derived from company + role (provided by the caller), and return the saved `Path`.

### Signature

```python
def tailor_resume(
    resume_text: str,
    job_analysis: JobAnalysis,
    company: str,
    role: str,
) -> Path:
    ...
```

### Acceptance criteria

- Saved markdown file exists under `output/tailored_resumes/`.
- Filename is slugified (lowercase, alphanumeric + hyphens only).

---

## Prompt 7 — Cover Letter Generation Chain (`chains/cover_letter.py`)

Implement `generate_cover_letter(resume_text: str, job_description: str, company: str, role: str) -> Path`.

### Requirements

1. Build a LangChain prompt that writes a **professional, personalized cover letter** (no generic templates):
   - Hook: mention something specific about the company or role.
   - Body: tie 2–3 resume achievements directly to the job requirements.
   - Close: express enthusiasm and a call to action.
2. Accept `resume_text`, `job_description`, `company`, and `role`.
3. Return the generated text and save it to `COVER_LETTERS_DIR` as a `.md` file with a slugified filename (`{company}-{role}-cover-letter.md`).
4. Return the saved `Path`.

### Acceptance criteria

- Markdown file written to `output/cover_letters/`.
- Filename slugified consistently with Prompt 6.

---

## Prompt 8 — Follow-Up Drafting Chain (`chains/followup.py`)

Implement `draft_followup(application_row: dict[str, Any]) -> str`.

### Requirements

1. Accept a single application row dictionary (the same shape returned by `get_followups_due` from `utils/tracker.py`).
2. Build a LangChain prompt that drafts a **short, polite follow-up email** (3–5 sentences max) referencing:
   - The role and company.
   - The date applied.
   - A brief reiteration of interest.
3. Return the plain-text email body as a string. Do **not** send it automatically.

### Bonus (optional but encouraged)

Also expose `draft_followup_all(due_rows: list[dict]) -> list[str]` that maps over multiple rows.

---

## Prompt 9 — Full Typer CLI (`main.py`)

Replace the minimal `verify` stub with a complete Typer application having these commands:

### Commands

1. **`verify`** (existing, keep)
   - Load config, print resolved paths, ensure resume file exists, print a preview via `preview_resume()`.

2. **`analyze <job_file> [--company NAME] [--role TITLE]`**
   - Read `job_file` (plain text `.txt` or `.md`).
   - Parse resume via `parse_resume()`.
   - Run `analyze_job()` → print `JobAnalysis` as a Rich JSON/table.
   - If `--company` and `--role` are provided, also run `tailor_resume()` and `generate_cover_letter()` automatically, save outputs, and print their paths.

3. **`apply --company NAME --role TITLE --source SOURCE --match-score SCORE [--notes TEXT]`**
   - Check `application_exists()`; abort with a friendly error if duplicate.
   - Call `generate_cover_letter()` (requires `--job-file` or a cached analysis).
   - Append to tracker via `add_application()`.
   - Print confirmation with row details.

4. **`followups`**
   - Query `get_followups_due()`.
   - For each due row, call `draft_followup()` and print the draft inline (Rich panel per follow-up).

5. **`tracker`**
   - Simply call `show_tracker()`.

### UX requirements

- Use `typer` with `rich` printing throughout.
- All file-path arguments should accept `str` or `Path` and validate existence where applicable.
- Consistent error handling: `typer.Exit(code=1)` on fatal errors with a colored message.
- Help text on every command.

---

## Prompt 10 — Cross-File Wiring Review + README

### Wiring review

1. Trace every import across the project:
   - `config` is imported everywhere; ensure no circular imports.
   - `chains/*` import `get_llm` from `chains.llm`; ensure no accidental import of heavy modules at startup.
   - `main.py` imports from both `chains` and `utils`; verify it doesn't break if `langchain-ollama` is missing (graceful import guards are acceptable).
2. Add `__all__` declarations to each public module (`chains/__init__.py`, `utils/__init__.py`).
3. Ensure `.gitignore` still covers new output artifacts.

### README

Write a root-level `README.md` containing:

1. **Project title & one-liner** — what this tool does.
2. **Setup** — clone, `pip install -r requirements.txt`, create `.env` from `.env.example`, place resume in `resume/resume.pdf`.
3. **Quick-start commands** — copy-pasteable examples for:
   - `python -m main verify`
   - `python -m main analyze job.txt --company "Acme" --role "Engineer"`
   - `python -m main apply --company "Acme" --role "Engineer" --source "LinkedIn" --match-score 85`
   - `python -m main followups`
   - `python -m main tracker`
4. **Architecture diagram** (ASCII is fine) showing flow: `resume.pdf` → `parse_resume` → `analyze_job` → `tailor_resume` + `generate_cover_letter` → `tracker`.
5. **Environment variables table** — every `.env` key, default, and purpose.
6. **Troubleshooting** — common issues (Ollama not running, empty PDF, missing `.env`).

---

## Style & Quality Gates (Apply to All Prompts)

- **Docstrings**: Every public function gets a PEP 257 docstring with `Args`, `Returns`, and `Raises` where applicable.
- **Typing**: Use `from __future__ import annotations` and modern `list[str]`, `str | None`, etc.
- **Paths**: Use `pathlib.Path`; never raw string concatenation for file paths.
- **Error handling**: Fail fast with informative exceptions; never swallow errors silently.
- **Rich formatting**: Prefer `rich.console.Console` and `rich.table.Table` for all CLI output.
- **Commit message format**: `feat(<scope>): <summary>` + bullet list of changes. Always end with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- **Changelog**: After each prompt, prepend a dated section to `docs/CHANGELOG.md` summarizing the changes.
- **Current task file**: Update `docs/CURRENT_TASK.md` — move completed items to `## Completed` and unfinished items to `## Next`.

---

## Suggested Batch Order

Because the chains have dependencies, implement in this order:

1. Prompt 5 (`analyzer.py` + `JobAnalysis`) — foundation for everything.
2. Prompt 7 (`cover_letter.py`) — independent of `tailorer`, can run in parallel with Prompt 6.
3. Prompt 6 (`tailorer.py`) — depends on `JobAnalysis`.
4. Prompt 8 (`followup.py`) — lightweight, can run anytime after Prompt 5.
5. Prompt 9 (`main.py`) — wires everything together.
6. Prompt 10 (`README.md` + review) — final polish.
