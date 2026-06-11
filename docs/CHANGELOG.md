# Changelog

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
