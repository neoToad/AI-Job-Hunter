# Current Task

## Step: Prompt 5 — Job Analyzer Chain

### What I'm actively working on
- Implementing `chains/analyzer.py` with:
  - `JobAnalysis` Pydantic model (company, role, must_have, nice_to_have, red_flags, match_score, matching_skills, missing_skills, recommendation, summary)
  - `analyze_job(resume: str, job_description: str) -> JobAnalysis` using ChatPromptTemplate + JsonOutputParser
  - Temperature 0.1 for consistent structured output
  - Prompt instructs honesty: never invent skills the candidate doesn't have

### Next step after this
- Prompt 6: Resume Tailorer Chain (`chains/tailorer.py`)

### Blockers
- None.
