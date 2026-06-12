# Current Task

## Prompt 38: Shared analysis display formatter

**Status:** In progress

**What I'm doing:**
Adding a `JobAnalysis.to_display_dict()` method in `chains/analyzer.py` that returns a structured dict of list-based sections (`must_have`, `matching_skills`, `missing_skills`, `red_flags`, `nice_to_have`). Then updating `main.py:_display_analysis()` and `app.py:analyze mode` to render from this shared formatter, removing duplicated field-access logic.

**Next step:**
Edit `chains/analyzer.py`, `main.py`, and `app.py`, run syntax checks, commit with message `[Prompt 38] Shared analysis display formatter`, and push.

**Blockers:** None.
