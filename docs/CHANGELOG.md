# Changelog

## 2026-06-11 — feat: scaffold job_search_tool project (Prompt 1)

- Created `job_search_tool/` directory tree (chains/, utils/, output/{cover_letters,tailored_resumes}/, resume/, data/)
- Added `requirements.txt` with langchain, langchain-ollama, langchain-community, pdfplumber, openpyxl, typer[all], rich, python-dotenv, pydantic, requests
- Added `.env.example` with OLLAMA_BASE_URL (with commented Ollama Cloud Pro URL), OLLAMA_MODEL, RESUME_PATH, TRACKER_PATH, OUTPUT_DIR
- Implemented `config.py` — loads .env via python-dotenv, exposes Path constants (RESUME_PATH, TRACKER_PATH, OUTPUT_DIR, COVER_LETTERS_DIR, TAILORED_RESUMES_DIR), creates output dirs on import, resolves relative paths against project root
- Added placeholder modules: `chains/{llm,analyzer,tailorer,cover_letter,followup}.py`, `utils/{resume_parser,tracker}.py`
- Added minimal `main.py` Typer stub with `verify` command (full CLI deferred to Prompt 9)
- Added `.gitkeep` files in `resume/` and `data/` to preserve empty layout
- Added root `.gitignore` (Python/IDE/OS noise, `.env` files, `resume.pdf`, `tracker.xlsx`, generated output files; keeps empty output subdirs via `.gitkeep`)
