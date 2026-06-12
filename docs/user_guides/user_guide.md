# User Guide

A day-in-the-life workflow for the Job Search CLI Tool.

---

## Daily Workflow

### 1. Find a Job Posting
Browse LinkedIn, Indeed, Adzuna, or company career pages. Copy the full job description text, or grab the posting URL.

### 2. Analyze the Fit

**Option A — paste directly:**
```bash
$ python main.py analyze
Paste job description, then press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done:
```

**Option B — from a URL:**
```bash
$ python main.py analyze --url https://jobs.example.com/posting
```

**Expected output:**
```
┌─────────────────────────────────┐
│ Job Analysis                    │
└─────────────────────────────────┘

Acme Corp — Senior Python Engineer
Match Score: ✅ 82/100
Recommendation: apply

Summary: Strong fit. Candidate has 5+ years of Python and Django,
which are must-haves. Missing AWS exposure, but role lists it as
nice-to-have.

Matching Skills
  ✔ Python
  ✔ Django
  ✔ REST API design

Missing Skills
  ✘ AWS Lambda
  ✘ Kubernetes

Red Flags
  ⚠ Requires on-site 5 days/week

Must-Have Requirements
  3+ years Python
  Experience with relational databases
  Bachelor's degree or equivalent experience

Nice-to-Have
  AWS experience
  CI/CD pipelines
```

**How to interpret the score:**
- **≥ 70** → Strong fit. Apply with confidence.
- **50 – 69** → Stretch role. Apply if you're genuinely interested and can address 1–2 missing skills in the cover letter.
- **< 50** → Poor fit. Consider skipping unless there's a strong personal reason to apply.

---

### 3. Run the Full Application Pipeline

If the score looks good, run `apply`:

```bash
$ python main.py apply --url https://jobs.example.com/posting
```

The tool will:
1. Parse your resume.
2. Analyze the job (same as above).
3. Ask if you want to continue.
4. Tailor your resume.
5. Generate a cover letter.
6. Save both to `output/`.
7. Log the application in `data/tracker.xlsx`.

**Summary panel at the end:**
```
┌─────────────────────────────────┐
│ Summary                         │
└─────────────────────────────────┘

Application logged!

Tailored resume: output/tailored_resumes/resume_acme_corp_senior_python_engineer_2026-06-12.txt
Cover letter:    output/cover_letters/cover_letter_acme_corp_senior_python_engineer_2026-06-12.txt
Tracker:         data/tracker.xlsx
```

**Dry run** (analyze only, nothing saved):
```bash
$ python main.py apply --dry-run --url https://jobs.example.com/posting
```

---

### 4. Track the Application

View your tracker:
```bash
$ python main.py tracker --show
```

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Job Application Tracker                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ Company      │ Role                    │ Date Applied │ Status       │
├──────────────────────────────────────────────────────────────────────────┤
│ Acme Corp    │ Senior Python Engineer  │ 2026-06-12   │ Applied      │
│ Beta Inc     │ Backend Developer       │ 2026-06-10   │ Interviewing │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 5. Update Status After Hear Back

Got an interview? Update the tracker:
```bash
$ python main.py status --company "Acme Corp" --role "Senior Python Engineer" --status "Interviewing"
```

Valid statuses: `Applied`, `Interviewing`, `Offer`, `Rejected`, `Withdrawn`.

---

### 6. Follow Up

After 2 weeks with no response, draft a follow-up email:

```bash
$ python main.py followup
```

The tool lists applications whose follow-up date has arrived. Pick one by number:

```
Follow-ups Due
┌────┬───────────┬───────────────────────┬──────────────┬───────────────┐
│  # │ Company   │ Role                  │ Date Applied │ Follow-up Date│
├────┼───────────┼───────────────────────┼──────────────┼───────────────┤
│  1 │ Acme Corp │ Senior Python Engineer│ 2026-06-12   │ 2026-06-26    │
└────┴───────────┴───────────────────────┴──────────────┴───────────────┘
Select application by number: 1
```

The drafted email appears in a panel. You can save it to a file if you like.

---

### 7. Edit or Delete Tracker Entries

**Edit a note:**
```bash
$ python main.py tracker --edit --company "Acme Corp" --role "Senior Python Engineer" --field "Notes" --value "Recruiter said they'd reply by Friday"
```

**Delete an entry:**
```bash
$ python main.py tracker --delete --company "Acme Corp" --role "Senior Python Engineer"
Are you sure you want to delete this entry? [y/N]: y
```

---

## Using the Streamlit UI

For a visual interface, run:
```bash
$ streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

**Analyze Job mode:**
- Paste the description in the big text box.
- Click **Analyze**.
- See the match score, recommendation badge, and expandable sections for requirements and skills.

**Full Application mode:**
- Paste the description.
- Optionally check **Dry run** to preview without saving.
- Click **Apply**.
- Watch the progress bar advance through analysis → tailoring → cover letter.
- If the app detects a duplicate in the tracker, a warning appears with a confirmation checkbox.
- After completion, editable text areas show the cover letter and tailored resume. You can tweak them and re-save manually if needed.

---

## Tips for Productivity

- **Batch analyze** — Collect 5–10 job descriptions in text files, then run `analyze --file` on each to quickly filter worth-apply roles.
- **Use `--skip-tailor`** if you already have a strong resume and just want a cover letter + tracker log.
- **Keep a notes log** — Use `tracker --edit` to record every interaction (phone screen, recruiter name, next steps) so nothing falls through the cracks.
