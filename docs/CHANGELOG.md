# Changelog

## 2026-06-11 — feat: Wiring review, error handling, and README (Prompt 10)

- Reviewed all imports across the project for consistency
- Confirmed every chain file imports `get_llm` from `chains.llm`
- Confirmed tracker handles missing `tracker.xlsx` gracefully (creates on first write, returns empty lists when missing)
- Confirmed `main.py` handles exceptions gracefully: resume/Ollama/LLM errors print helpful messages and exit with `typer.Exit(1)` instead of raw tracebacks
- Added optional `source` prompt to the `apply` command for better tracker data quality
- Fixed `tracker` command to only display the table when `--show` is passed; otherwise prints a usage hint
- Wrote `README.md` with setup instructions, local Ollama guide (`ollama pull llama3.1`, `ollama serve`), Ollama Cloud Pro configuration, and CLI command examples

## 2026-06-11 — feat: Full Typer CLI entry point (Prompt 9)

- Rewrote `main.py` as a complete Typer app with Rich formatting and `SpinnerColumn` progress indicators
- `verify`: checks resume PDF parseability via `preview_resume`, hits Ollama `/api/tags` with optional Bearer auth, confirms configured model exists
- `analyze`: reads multi-line job description until `END`, runs `analyze_job()`, displays match score in color (green ≥70, yellow ≥50, red <50), matching skills with ✔, missing skills with ✘, red flags with ⚠, plus must-have / nice-to-have tables
- `apply`: full pipeline — parse → collect JD → analyze → confirm → duplicate check → optional tailor (`--skip-tailor`) → generate cover letter → save to `output/` with `make_slug` filenames → optional notes → update tracker → print summary panel
- `followup`: supports `--company/--role/--date` or interactive picker from `get_followups_due()` with numbered selection; drafts email and offers to save
- `tracker --show`: displays tracker via `show_tracker()`
- Added `utils/helpers.py` with `make_slug(company, role)` — lowercase, spaces→underscores, slashes→dashes

## 2026-06-11 — feat: Follow-up Email Chain (Prompt 8)

- Implemented `chains/followup.py` with `draft_followup(company, role, date_applied)`
- Uses ChatPromptTemplate + StrOutputParser at temperature 0.4
- Constrained to under 100 words
- Explicitly forbids pushy or groveling language
- References the specific role and politely asks about the hiring timeline

## 2026-06-11 — feat: Cover Letter Chain (Prompt 7)

- Implemented `chains/cover_letter.py` with `generate_cover_letter(resume, job_description, analysis)`
- Uses ChatPromptTemplate + StrOutputParser at temperature 0.5 for natural writing
- Constrained to 3–4 paragraphs and under 400 words
- Explicitly forbids generic filler phrases like "I am excited to apply" / "I am a team player"
- Instructs model to map specific resume evidence to specific job requirements
- Consumes `JobAnalysis.company`, `role`, `must_have`, and `matching_skills`

## 2026-06-11 — feat: Resume Tailorer Chain (Prompt 6)

- Implemented `chains/tailorer.py` with `tailor_resume(resume, job_description, analysis)`
- Uses ChatPromptTemplate + StrOutputParser at temperature 0.2
- Instructs LLM to rewrite bullet points using job-posting keywords, preserve all resume sections, and use strong action verbs
- Explicitly forbids inventing experience or skills the candidate does not have
- Consumes `JobAnalysis.must_have` and `JobAnalysis.matching_skills` for context

## 2026-06-11 — feat: Job Analyzer Chain (Prompt 5)

- Implemented `chains/analyzer.py` with `JobAnalysis` Pydantic model
- Fields: company, role, must_have, nice_to_have, red_flags, match_score (0–100), matching_skills, missing_skills, recommendation (Literal["apply","skip","stretch"]), summary
- `analyze_job(resume, job_description)` uses ChatPromptTemplate + JsonOutputParser with temperature 0.1
- Prompt instructs the LLM to be honest and never invent skills the candidate doesn't have
- Returns a validated `JobAnalysis` instance

## 2026-06-11 — feat: application tracker in openpyxl (Prompt 4)

- Implemented `utils/tracker.py` backed by an `.xlsx` workbook via openpyxl
- `_get_or_create_workbook(path)` loads existing workbook or creates one with bold header row (`Company`, `Role`, `Date Applied`, `Source`, `Match Score`, `Status`, `Follow-up Date`, `Notes`, `Cover Letter Path`)
- `application_exists(path, company, role) -> bool` performs case-insensitive duplicate detection on company + role pair
- `add_application(...)` appends a new row, auto-filling `Date Applied` as today, `Status` as `"Applied"`, and `Follow-up Date` as 14 days from today
- `show_tracker(path)` renders all rows as a formatted Rich table via `rich.table.Table`
- `get_followups_due(path) -> list[dict]` returns every row where `Status == "Applied"` and `Follow-up Date` is today or earlier, keyed by column header

## 2026-06-11 — feat: scaffold job_search_tool project (Prompt 1)

- Created `job_search_tool/` directory tree (chains/, utils/, output/{cover_letters,tailored_resumes}/, resume/, data/)
- Added `requirements.txt` with langchain, langchain-ollama, langchain-community, pdfplumber, openpyxl, typer[all], rich, python-dotenv, pydantic, requests
- Added `.env.example` with OLLAMA_BASE_URL (with commented Ollama Cloud Pro URL), OLLAMA_MODEL, RESUME_PATH, TRACKER_PATH, OUTPUT_DIR
- Implemented `config.py` — loads .env via python-dotenv, exposes Path constants (RESUME_PATH, TRACKER_PATH, OUTPUT_DIR, COVER_LETTERS_DIR, TAILORED_RESUMES_DIR), creates output dirs on import, resolves relative paths against project root
- Added placeholder modules: `chains/{llm,analyzer,tailorer,cover_letter,followup}.py`, `utils/{resume_parser,tracker}.py`
- Added minimal `main.py` Typer stub with `verify` command (full CLI deferred to Prompt 9)
- Added `.gitkeep` files in `resume/` and `data/` to preserve empty layout
- Added root `.gitignore` (Python/IDE/OS noise, `.env` files, `resume.pdf`, `tracker.xlsx`, generated output files; keeps empty output subdirs via `.gitkeep`)

## 2026-06-11 — feat: LLM factory (Prompt 2)

- Implemented `get_llm(temperature: float = 0.3) -> ChatOllama` in `chains/llm.py`
- Reads `OLLAMA_BASE_URL` and `OLLAMA_MODEL` from `config.py`; forwards `OLLAMA_API_KEY` as a Bearer authorization header when present (for Ollama Cloud Pro)
- Single import point for every chain — swapping models/URLs is a one-line change in `.env`

## 2026-06-11 — feat: resume PDF parser (Prompt 3)

- Implemented `parse_resume(path: Path) -> str` in `utils/resume_parser.py` using pdfplumber
- Pages are joined with double newlines; raises `FileNotFoundError` on a missing path
- Prints a rich-formatted warning (via `rich.console.Console`) for any page that returns no text — likely image-based and a candidate for OCR
- Raises `ValueError` when the whole document yields no text
- Implemented `preview_resume(path: Path, chars: int = 500) -> str` that reuses `parse_resume` and returns a stripped, length-capped snippet for quick verification
