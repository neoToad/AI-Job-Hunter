# Current Task

## Prompt 12 — Fix: First-Run Experience

**What I'm actively working on:**
Adding a Typer callback (`@app.callback()`) in `main.py` that:
1. Checks if `resume/resume.pdf` exists
2. Checks if `.env` exists (or environment variables are set)
3. If either is missing, prints a friendly Rich Panel explaining first-run steps
4. Does NOT block execution — just prints the hint and continues

**Next step:** Commit Prompt 12, then move to Prompt 13.
