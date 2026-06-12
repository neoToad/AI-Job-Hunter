# Current Task

## Prompt 16 — Refactor: Centralized Error Handling

**What I'm actively working on:**
1. Creating `handle_error(message: str, hint: str = "")` in `utils/helpers.py` that prints message in red with ✗ prefix, prints hint in dim text, and calls `raise typer.Exit(1)`.
2. Wrapping all LLM chain calls in `main.py` try/except for:
   - `ConnectionError` → "Cannot reach Ollama. Is it running? Try: ollama serve"
   - General `Exception` → print error and suggest running `verify`
3. Wrapping resume parsing in try/except for:
   - `FileNotFoundError` → "Resume not found at {path}. Place your PDF at resume/resume.pdf"
   - `ValueError` → "Could not parse resume. Try re-saving it as a text-based PDF."
4. Ensuring no raw Python tracebacks are shown to users during normal operation.

**Next step:** Commit Prompt 16, then move to Prompt 17.
