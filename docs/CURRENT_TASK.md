# Current Task

## Next
- Prompt 4: implement openpyxl tracker in `utils/tracker.py`
- Prompt 5: implement `analyze_job()` chain + `JobAnalysis` Pydantic model
- Prompt 6: implement `tailor_resume()` chain
- Prompt 7: implement `generate_cover_letter()` chain
- Prompt 8: implement `draft_followup()` chain
- Prompt 9: build full Typer CLI in `main.py` (verify, analyze, apply, followup, tracker)
- Prompt 10: cross-file wiring review + README

## Completed
- Prompt 1: scaffolded `job_search_tool/` directory structure, requirements.txt, .env.example, config.py, placeholder chain/utility modules, minimal main.py verify stub. Config loads via python-dotenv, output dirs created on import.
- Added root `.gitignore` covering Python/IDE/OS noise, .env files, the user's resume.pdf and tracker.xlsx, and generated output files (but keeping empty output subdirs via .gitkeep).
- Prompt 2: implemented `get_llm(temperature=0.3)` in `chains/llm.py` returning a `ChatOllama` configured from `config.OLLAMA_BASE_URL` and `config.OLLAMA_MODEL`; forwards `OLLAMA_API_KEY` as a Bearer header for Ollama Cloud Pro when set.
- Prompt 3: implemented `parse_resume(path)` and `preview_resume(path, chars=500)` in `utils/resume_parser.py` using pdfplumber — raises FileNotFoundError on missing files, prints rich warning for any page that returns no text (likely image-based), and raises ValueError if the whole document is empty.
- Prompt 4: implemented `utils/tracker.py` with `_get_or_create_workbook`, `application_exists`, `add_application`, `show_tracker`, and `get_followups_due`. Uses openpyxl for persistence, bold headers, auto-filled dates (today + 14 days), and Rich tables for display.

## Tests
- `python -c "import config"` succeeds; paths resolve relative to project root; output dirs created on import.
- `python -c "from chains.llm import get_llm; print(get_llm())"` not run yet — `langchain-ollama` is not installed in this env (install via `pip install -r requirements.txt` before Prompt 3).
- AST-validated `utils/resume_parser.py` (pdfplumber is not installed in this env, so an end-to-end parse against a real PDF was not run).

## Blockers
- None.
