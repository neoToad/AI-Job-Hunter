# Current Task

## Next
- Prompt 2: implement `get_llm()` in `chains/llm.py` (ChatOllama from config)
- Prompt 3: implement `parse_resume()` and `preview_resume()` in `utils/resume_parser.py`
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

## Tests
- `python -c "import config"` succeeds; paths resolve relative to project root; output dirs created on import.
- Full CLI not yet testable — typer/rich/langchain not installed in this env (install via `pip install -r requirements.txt` before Prompt 2).

## Blockers
- None.
