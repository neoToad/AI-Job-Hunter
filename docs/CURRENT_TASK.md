# Current Task

## Step 5 — Phase B: Update `tailorer_system.txt` prompt

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Updating the system prompt to instruct the LLM to return valid JSON with keys:
- contact
- summary
- experience
- education
- skills

And to forbid Markdown and plain text.

**Next:** Refactor `tailor_resume` chain to use JsonOutputParser (Step 6).
