# Current Task

## Prompt 13 — Fix: Job Description Validation

**What I'm actively working on:**
1. Adding `validate_job_description(jd: str) -> tuple[bool, str]` in `chains/analyzer.py`.
   - Check minimum length (100 chars)
   - Check for job-posting signals: "responsibilities", "requirements", "qualifications", "experience", "skills", "role", "position", "job"
   - Check it's not just a URL or single line
   - Return (True, "") if valid, (False, "reason") if not
2. Calling this validation in `main.py` `analyze` and `apply` commands after JD collection.
3. If invalid, printing reason in yellow and asking user "Continue anyway? y/n"

**Next step:** Commit Prompt 13, then move to Prompt 14.
