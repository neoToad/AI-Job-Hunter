# Current Task

## Prompt 15 — Refactor: Prompt Templates to Separate Files

**What I'm actively working on:**
Refactoring all LLM prompt templates out of chain files into plain `.txt` files in a new `prompts/` directory.

Files to create:
- prompts/analyzer_system.txt
- prompts/analyzer_human.txt
- prompts/tailorer_system.txt
- prompts/tailorer_human.txt
- prompts/cover_letter_system.txt
- prompts/cover_letter_human.txt
- prompts/followup_system.txt
- prompts/followup_human.txt

In each chain file, load prompts using:
```python
def _load_prompt(name: str) -> str:
    return (Path(__file__).parent.parent / "prompts" / name).read_text()
```

**Next step:** Commit Prompt 15, then move to Prompt 16.
