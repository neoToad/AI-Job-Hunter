# Job Search CLI Tool — Prompts 21–24

## How to Use
Run these after Prompts 1–20 are complete.

---

## Prompt 21 — Fix: Explicit Prompt File Contents

```
In the job_search_tool project, populate the prompts/ directory with the exact
content for each file. Do not invent content — use exactly what is specified below.

Create prompts/analyzer_system.txt:
"""
You are an expert job application coach. Analyze the job description and
compare it against the candidate's resume. Respond ONLY with valid JSON matching this exact structure:

{
  "company": "company name",
  "role": "job title",
  "must_have": ["list of non-negotiable requirements"],
  "nice_to_have": ["list of preferred but optional requirements"],
  "red_flags": ["e.g. unrealistic experience demands, vague role, high turnover signals"],
  "match_score": 0-100,
  "matching_skills": ["skills the candidate has that match"],
  "missing_skills": ["required skills the candidate lacks"],
  "recommendation": "apply" or "skip" or "stretch",
  "summary": "2-3 sentence plain English summary of fit"
}

Be honest and realistic. Do not invent skills the candidate does not have.
"""

Create prompts/analyzer_human.txt:
"""
RESUME:
{resume}

JOB DESCRIPTION:
{job_description}
"""

Create prompts/tailorer_system.txt:
"""
You are an expert resume writer specializing in ATS optimization.
Rewrite the candidate's resume bullet points to better match the job description,
using the exact keywords and phrasing from the job posting where truthful and applicable.

Rules:
- Never invent experience or skills the candidate does not have
- Keep the same meaning, just improve keyword alignment
- Use strong action verbs
- Be specific and quantify where the original resume does
- Return the full rewritten resume text, preserving all sections and headings
"""

Create prompts/tailorer_human.txt:
"""
ORIGINAL RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

KEY REQUIREMENTS TO TARGET:
{must_have}

MATCHING SKILLS TO EMPHASIZE:
{matching_skills}

Rewrite the resume to better match this role.
"""

Create prompts/cover_letter_system.txt:
"""
You are an expert cover letter writer. Write compelling, specific cover letters
that map the candidate's real experience directly to the job's key requirements.

Rules:
- Never use generic filler phrases like "I am excited to apply" or "I am a team player"
- Every paragraph must reference specific experience from the resume
- Map specific resume evidence to specific job requirements
- Keep it to 3-4 paragraphs, under 400 words
- Professional but human tone, not robotic
- End with a confident but not arrogant closing
"""

Create prompts/cover_letter_human.txt:
"""
RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

COMPANY: {company}
ROLE: {role}

KEY REQUIREMENTS TO ADDRESS:
{must_have}

CANDIDATE'S MATCHING STRENGTHS:
{matching_skills}

Write a tailored cover letter for this specific role.
"""

Create prompts/followup_system.txt:
"""
You are a professional career coach. Write a brief, polite follow-up email
for a job application.

Rules:
- Keep it under 100 words
- Polite and professional, not pushy
- Reference the specific role applied for
- Express continued interest
- Ask politely about the timeline
- Do not grovel or over-apologize for following up
"""

Create prompts/followup_human.txt:
"""
I applied for the {role} position at {company} on {date_applied}.
I have not heard back yet. Please write a follow-up email.
"""

After creating all files, verify that each chain file correctly loads its
corresponding prompt files and that all {placeholder} variables match what
the chain actually passes in.
```

---

## Prompt 22 — Feature: File & URL Input for CLI

```
In `main.py`, improve the job description input method for the `analyze` and
`apply` commands. Replace the current "paste until END" approach with a proper
input helper that supports three modes:

1. --file path/to/job.txt
   Read the job description from a plain text file

2. --url https://jobs.example.com/posting
   Fetch the page using requests, parse with BeautifulSoup, extract the main
   body text (strip nav, headers, footers, scripts, styles), and use that as
   the job description. Print a warning if the extracted text is under 200 chars.

3. No flag (default)
   Fall back to the existing interactive paste method, but improve it:
   instead of "type END on a blank line", use a cleaner prompt that says
   "Paste job description, then press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done"
   and reads from sys.stdin until EOF.

Create a shared helper function `get_job_description(file, url) -> str` that
handles all three modes and is called by both the `analyze` and `apply` commands.

Add beautifulsoup4 and lxml to requirements.txt if not already present.
```

---

## Prompt 23 — Feature: Tracker Delete & Edit

```
In `utils/tracker.py`, add two new functions:

1. `delete_application(path: Path, company: str, role: str) -> bool`
   - Find the row matching company + role (case-insensitive)
   - Delete it from the spreadsheet
   - Save the workbook
   - Return True if found and deleted, False if not found

2. `edit_application(path: Path, company: str, role: str, field: str, value: str) -> bool`
   - Find the row matching company + role (case-insensitive)
   - Update the specified field (column name) with the new value
   - Valid fields: Source, Match Score, Status, Follow-up Date, Notes, Cover Letter Path
   - Save the workbook
   - Return True if updated, False if row or field not found

In `main.py`, expose these as tracker subcommands:

python main.py tracker --delete --company "Acme" --role "Engineer"
  → Confirm with "Are you sure you want to delete this entry? y/n" before deleting

python main.py tracker --edit --company "Acme" --role "Engineer" --field "Notes" --value "Had phone screen"
  → Print confirmation of what was changed
```

---

## Prompt 24 — Feature: Streamlit UI

```
Create a new file `app.py` in the project root. This is a Streamlit app that
provides a UI for the two commands where copy-pasting is most useful: analyze and apply.

Add streamlit to requirements.txt.

The app should have a sidebar with:
- A title "Job Search Assistant"
- Radio buttons to choose mode: "Analyze Job" or "Full Application"
- A text input for Job Source (e.g. LinkedIn, Adzuna) — only shown in Full Application mode

The main panel should have:
- A large st.text_area for pasting the job description (height=300)
- A checkbox for "Dry run (analyze only, don't save)" — only in Full Application mode
- A primary button: "Analyze" or "Apply" depending on mode

When the button is clicked:

In Analyze mode:
- Call parse_resume() and analyze_job() using the existing chain functions
- Display results using st.metric() for the match score
- Use st.success / st.warning / st.error for recommendation (apply/stretch/skip)
- Show must-have requirements, matching skills, missing skills, and red flags
  in organized st.expander() sections

In Full Application mode (not dry run):
- Run the full pipeline: analyze → tailor → cover letter → tracker update
- Show a st.progress() bar advancing through each step
- Display the generated cover letter in a st.text_area (editable, so user can tweak)
- Display the tailored resume in a second st.text_area
- Show a success banner when tracker is updated
- If the application already exists in the tracker, show a st.warning and ask
  the user to confirm via a st.checkbox before proceeding

In Dry Run mode:
- Only run analyze_job() and display results, same as Analyze mode
- Show a banner: "Dry run — nothing saved"

The app should import directly from chains/ and utils/ — no duplication of logic.
All file saving and tracker updates should use the exact same functions as the CLI.

To run: streamlit run app.py
```
