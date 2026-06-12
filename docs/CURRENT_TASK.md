# Current Task

## Step 4 — Phase B: Define `TailoredResume` Pydantic models

**Status:** In progress  
**Branch:** `feature/job-search-output-formats`

**What:** Adding Pydantic models to `chains/tailorer.py`:
- `ExperienceEntry` — title, company, dates, bullets
- `TailoredResume` — contact, summary, experience, education, skills

These models will be used by `JsonOutputParser` in Step 6.

**Next:** Update `tailorer_system.txt` prompt (Step 5).
