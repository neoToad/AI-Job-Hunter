# Current Task

## Step 14: Test CLI (`main.py`)

**Status:** In progress

**What I'm doing:**
- Created `tests/test_cli.py` with Typer `CliRunner` integration tests:
  - `verify` exits 1 when resume missing
  - `verify` exits 0 when resume and Ollama are OK
  - `analyze` with `--file` and valid input exits 0
  - `tracker --show` on empty tracker exits 0
  - `tracker --delete` with confirmation input exits 0

**Next step:** Commit and push, then move to Step 15 (Add CI workflow).
