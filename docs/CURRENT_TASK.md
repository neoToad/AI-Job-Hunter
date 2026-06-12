# Current Task

## Step: Prompt 7 — Cover Letter Chain

### What I'm actively working on
- Implementing `chains/cover_letter.py` with:
  - `generate_cover_letter(resume: str, job_description: str, analysis: JobAnalysis) -> str`
  - ChatPromptTemplate taking resume, job description, company, role, must-have requirements, and matching skills
  - Instructs LLM to write a 3–4 paragraph cover letter under 400 words
  - Explicitly forbids generic filler phrases like "I am excited to apply" or "I am a team player"
  - Instructs model to map specific resume evidence to specific job requirements
  - Temperature 0.5 for more natural writing
  - Return plain string via StrOutputParser

### Next step after this
- Prompt 8: Follow-up Email Chain (`chains/followup.py`)

### Blockers
- None.
