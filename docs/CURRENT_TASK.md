# Current Task

## Prompt 31: Extract _load_prompt to shared helper

**Status:** In progress

**What I'm doing:**
Creating a new `chains/utils.py` module with a shared `load_prompt(name: str) -> str` helper. Then updating all four chain modules (analyzer, tailorer, cover_letter, followup) to import from it instead of duplicating the 3-line `_load_prompt()` function.

**Next step:**
Create `chains/utils.py`, update the four chain modules, run a smoke test (`python -m main --help`), commit with message `[Prompt 31] Extract _load_prompt to shared helper in chains/utils.py`, and push.

**Blockers:** None.
