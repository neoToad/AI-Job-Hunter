# Current Task

## Step: Prompt 6 — Resume Tailorer Chain

### What I'm actively working on
- Implementing `chains/tailorer.py` with:
  - `tailor_resume(resume: str, job_description: str, analysis: JobAnalysis) -> str`
  - ChatPromptTemplate taking original resume, job description, must-have requirements, and matching skills
  - Instructs LLM to rewrite bullet points using keywords from the job posting
  - Explicitly forbids inventing experience the candidate doesn't have
  - Tells the model to preserve all resume sections and use strong action verbs
  - Temperature 0.2
  - Return plain string via StrOutputParser

### Next step after this
- Prompt 7: Cover Letter Chain (`chains/cover_letter.py`)

### Blockers
- None.
