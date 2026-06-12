# Current Task

## Step: Prompt 10 — Wiring & Testing + README

### What I'm actively working on
- Review all files in `job_search_tool/` for:
  1. Correct and consistent imports (config as module, pathlib.Path)
  2. Every chain file imports `get_llm` from `chains.llm`
  3. Tracker correctly handles missing `tracker.xlsx`
  4. `main.py` handles exceptions gracefully (no raw tracebacks on resume/Ollama failures)
  5. Output slug helper is used consistently (`make_slug`)
- Fix any issues found
- Write `README.md` with setup instructions, Ollama local/cloud guides, and CLI examples

### Next step after this
- Final review, push branch, confirm all commits

### Blockers
- None.
