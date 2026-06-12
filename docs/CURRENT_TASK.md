# Current Task

## Prompt 18 — Best Practices: Config Validation

**What I'm actively working on:**
1. Adding `validate_config()` in `config.py` that checks:
   - If `OLLAMA_MODEL` is not set or empty → warn "No model set, defaulting to llama3.1"
   - If `OLLAMA_BASE_URL` points to localhost but port 11434 is not open → warn "Ollama may not be running locally"
   - If `RESUME_PATH` does not exist → warn "Resume not found at {path}"
   - If `TRACKER_PATH` parent directory does not exist → create it silently
2. Calling `validate_config()` from `@app.callback()` in `main.py` so it runs once at startup.
3. All warnings printed via Rich, never blocking execution.

**Next step:** Commit Prompt 18, then move to Prompt 19.
