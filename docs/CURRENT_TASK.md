# Current Task

## Step: Prompt 8 — Follow-up Email Chain

### What I'm actively working on
- Implementing `chains/followup.py` with:
  - `draft_followup(company: str, role: str, date_applied: str) -> str`
  - ChatPromptTemplate taking company, role, and date_applied
  - Instructs LLM to write a polite follow-up email under 100 words
  - Explicitly says not to be pushy or grovel
  - Should reference the specific role and ask politely about the timeline
  - Temperature 0.4
  - Return plain string via StrOutputParser

### Next step after this
- Prompt 9: Build full Typer CLI in `main.py` (verify, analyze, apply, followup, tracker)

### Blockers
- None.
