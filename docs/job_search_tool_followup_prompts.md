# Job Search CLI Tool — Follow-up & Cleanup Prompts

## How to Use
Run these AFTER the 10 scaffold prompts are complete and the project is working.
These prompts handle fixes, hardening, and refactoring.

---

## Prompt 11 — Fix: Output Directory & Init Files

```
In the job_search_tool project, verify and fix the following:

1. Ensure `chains/__init__.py` and `utils/__init__.py` both exist (even if empty).
   These are required for Python to treat them as packages.

2. In `config.py`, make sure ALL of the following directories are created on import
   using `mkdir(parents=True, exist_ok=True)`:
   - output/
   - output/cover_letters/
   - output/tailored_resumes/
   - data/
   - resume/

3. In `main.py`, at the top of the `apply` command, wrap the output file save steps
   in a try/except that catches OSError and prints a helpful message if the directory
   can't be created or written to.
```

---

## Prompt 12 — Fix: First-Run Experience

```
In `main.py`, add a first-run check that runs automatically before any command executes.

Use a Typer callback (decorated with @app.callback()) that:
1. Checks if resume/resume.pdf exists
2. Checks if .env exists (or environment variables are set)
3. If either is missing, print a friendly Rich Panel explaining:
   - "Looks like this might be your first time running this tool."
   - Step 1: Copy .env.example to .env and fill in your settings
   - Step 2: Place your resume PDF at resume/resume.pdf
   - Step 3: Run `python main.py verify` to confirm everything works
4. Do NOT block execution — just print the hint and continue, so
   the `verify` command itself can still run and show detailed errors.
```

---

## Prompt 13 — Fix: Job Description Validation

```
In `chains/analyzer.py`, add a `validate_job_description(jd: str) -> tuple[bool, str]`
function that does a quick sanity check before running the full analysis chain.

It should check:
1. Minimum length (at least 100 characters)
2. Contains at least one of these signals: "responsibilities", "requirements",
   "qualifications", "experience", "skills", "role", "position", "job"
3. Is not just a URL or a single line

Return (True, "") if valid, or (False, "reason string") if not.

In `main.py`, call this validation in both the `analyze` and `apply` commands
after the job description is collected. If invalid, print the reason in yellow
and ask the user "This doesn't look like a complete job description. Continue anyway? y/n"
```

---

## Prompt 14 — Feature: --dry-run Flag

```
In `main.py`, add a `--dry-run` boolean flag to the `apply` command (default False).

When --dry-run is True:
- Run the job description validation
- Run the analyzer and display the full results (match score, skills, red flags)
- Print "Dry run complete — no files saved and tracker not updated."
- Exit without running the tailorer, cover letter generator, or tracker update

This lets the user quickly screen a job posting before committing to the full pipeline.

Example usage:
  python main.py apply --dry-run
```

---

## Prompt 15 — Refactor: Prompt Templates to Separate Files

```
Refactor the project so that all LLM prompt templates are stored as plain .txt files
in a new `prompts/` directory, rather than hardcoded as strings in the chain files.

Create:
  prompts/
  ├── analyzer_system.txt
  ├── analyzer_human.txt
  ├── tailorer_system.txt
  ├── tailorer_human.txt
  ├── cover_letter_system.txt
  ├── cover_letter_human.txt
  ├── followup_system.txt
  └── followup_human.txt

In each chain file, load the prompt text using a helper like:
  def _load_prompt(name: str) -> str:
      return (Path(__file__).parent.parent / "prompts" / name).read_text()

Benefits:
- Prompts can be edited without touching Python code
- Easier to iterate and improve prompt quality
- Cleaner chain files

Make sure all existing behavior is preserved after the refactor.
```

---

## Prompt 16 — Refactor: Centralized Error Handling

```
Refactor error handling in `main.py` to be consistent across all commands.

1. Create a utility function `handle_error(message: str, hint: str = "")` that:
   - Prints the message in red with an ✗ prefix
   - Prints the hint in dim text if provided
   - Calls raise typer.Exit(1)

2. Wrap all LLM chain calls in try/except blocks that catch:
   - ConnectionError → "Cannot reach Ollama. Is it running? Try: ollama serve"
   - Exception (general) → print the error message and suggest running `verify`

3. Wrap resume parsing in a try/except that catches:
   - FileNotFoundError → "Resume not found at {path}. Place your PDF at resume/resume.pdf"
   - ValueError → "Could not parse resume. Try re-saving it as a text-based PDF."

4. Make sure no raw Python tracebacks are ever shown to the user during normal operation.
   All errors should be friendly Rich-formatted messages.
```

---

## Prompt 17 — Best Practices: Type Hints & Docstrings

```
Review all Python files in the project and make the following improvements:

1. Add complete type hints to every function signature (parameters and return types)
   in utils/resume_parser.py, utils/tracker.py, and all chains/ files.

2. Add a one-line docstring to every public function that doesn't already have one.

3. In chains/analyzer.py, make sure the JsonOutputParser failure case is handled —
   if the LLM returns malformed JSON, catch the parse error and raise a clear
   ValueError with a message like: "AI returned unexpected format. Try running again."

4. Remove any unused imports across all files.

5. Make sure all string formatting uses f-strings consistently (not .format() or % formatting).
```

---

## Prompt 18 — Best Practices: Config Validation

```
In `config.py`, add a `validate_config()` function that checks for common
misconfiguration issues and prints warnings (not errors) using Rich:

1. If OLLAMA_MODEL is not set or is an empty string → warn "No model set, defaulting to llama3.1"
2. If OLLAMA_BASE_URL still points to localhost but the user is on a machine
   where port 11434 is not open → warn "Ollama may not be running locally"
3. If RESUME_PATH does not exist → warn "Resume not found at {path}"
4. If TRACKER_PATH parent directory does not exist → create it silently

Call validate_config() from the @app.callback() in main.py so it runs once
at startup before any command, but only print warnings (never block execution).
```

---

## Prompt 19 — Best Practices: Tracker Robustness

```
Improve the robustness of `utils/tracker.py`:

1. In `add_application()`, validate that company and role are non-empty strings
   before writing. Raise ValueError if either is empty.

2. In `show_tracker()`, handle the case where the spreadsheet has rows but all
   are empty (e.g. the user manually cleared it). Print "No applications found."

3. In `get_followups_due()`, handle corrupt or unexpected date formats gracefully —
   skip rows with unparseable dates rather than crashing.

4. Add an `update_status(path, company, role, new_status)` function that finds
   the matching row and updates the Status column. Valid statuses:
   "Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"

5. Expose `update_status` as a new CLI command in main.py:
   python main.py status --company "Acme" --role "Engineer" --status "Interviewing"
```

---

## Prompt 20 — Final Review

```
Do a final review of the entire job_search_tool project. Check for:

1. Circular imports — make sure no utils file imports from chains and no chain
   file imports from main.py

2. Consistent use of Path objects — no raw string paths anywhere, everything
   should use pathlib.Path

3. The .env.example file is complete and matches every value read in config.py

4. The prompts/ directory (if created in Prompt 15) has all 8 expected files
   and none are empty

5. Every CLI command has a help string that shows up in `python main.py --help`

6. The README.md covers all commands including the new ones added in these
   follow-up prompts (--dry-run, status update)

7. The output slug helper correctly handles edge cases:
   - Company names with special characters (e.g. "AT&T", "C3.ai")
   - Very long company or role names (truncate at 50 chars)

Fix anything found. Then run `python main.py verify` and confirm it exits cleanly.
```
