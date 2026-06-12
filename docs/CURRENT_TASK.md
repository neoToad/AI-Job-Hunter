# Current Task

## Prompt 14 — Feature: --dry-run Flag

**What I'm actively working on:**
Adding a `--dry-run` boolean flag to the `apply` command in `main.py` (default False).

When `--dry-run` is True:
- Run job description validation
- Run the analyzer and display full results (match score, skills, red flags)
- Print "Dry run complete — no files saved and tracker not updated."
- Exit without running tailorer, cover letter generator, or tracker update

Example: `python main.py apply --dry-run`

**Next step:** Commit Prompt 14, then move to Prompt 15.
