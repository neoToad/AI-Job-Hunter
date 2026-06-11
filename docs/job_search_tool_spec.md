# Job Search CLI Tool — Project Spec

## Overview

A personal CLI tool built with LangChain that automates and streamlines the job application process. It tailors resumes, generates cover letters, analyzes job descriptions, tracks applications, and drafts follow-up emails.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python |
| LLM Framework | LangChain |
| LLM (primary) | Llama 3.1 8B via Ollama (local) |
| LLM (fallback/upgrade) | Ollama Cloud Pro |
| CLI Framework | Typer |
| Terminal Output | Rich |
| Resume Parsing | pdfplumber |
| Spreadsheet | openpyxl |
| Config/Secrets | python-dotenv |

---

## Scope — V1 Features

### 1. Job Description Analyzer
- Parse a job posting (pasted text or URL)
- Extract must-have vs. nice-to-have requirements
- Identify red flags (e.g. inflated experience requirements)
- Output a match score against the user's resume
- Ask user to confirm before proceeding

### 2. Resume Tailorer
- Parse user's resume from PDF
- Rewrite bullet points to match job description keywords
- Optimized for ATS (applicant tracking systems)
- Save tailored version to `/output/tailored_resumes/`

### 3. Cover Letter Generator
- Uses RAG to pull the most relevant resume sections
- Maps specific resume evidence to specific job requirements
- Saves output to `/output/cover_letters/`

### 4. Application Tracker
- Auto-updates `tracker.xlsx` after each application
- Columns: Company, Role, Date Applied, Source, Match Score, Status, Follow-up Date, Notes, Cover Letter Path
- Deduplication check on Company + Role before inserting

### 5. Follow-up Email Drafter
- Triggered manually or based on tracker follow-up date
- Drafts a polite follow-up email for a given application
- Run via: `python main.py followup --company "Acme Corp"`

---

## Deferred to V2

- Interview prep brief (likely questions, talking points, company research)
- Salary research per role
- Live job fetching (Adzuna API, SerpAPI/Google Jobs)
- Glassdoor/company sentiment analysis
- Scheduled daily runs via cron

---

## Out of Scope

- LinkedIn scraping (ToS violations, aggressive anti-bot detection)
- Browser automation
- Any web frontend or GUI

---

## Project Structure

```
job_search_tool/
├── main.py                 # CLI entry point
├── config.py               # API keys, settings
├── resume/
│   └── resume.pdf          # user's resume
├── data/
│   └── tracker.xlsx        # application spreadsheet
├── output/
│   ├── cover_letters/      # generated letters
│   └── tailored_resumes/   # tailored resume versions
├── chains/
│   ├── analyzer.py         # job description analyzer
│   ├── tailorer.py         # resume tailorer
│   ├── cover_letter.py     # cover letter generator
│   └── followup.py         # follow-up email drafter
└── utils/
    ├── resume_parser.py    # PDF parsing
    └── tracker.py          # spreadsheet read/write
```

---

## CLI Commands

```bash
# Analyze a job posting
python main.py analyze --url https://jobs.example.com/posting

# Run the full application pipeline
python main.py apply --url https://jobs.example.com/posting

# View application tracker
python main.py tracker --show

# Draft a follow-up email
python main.py followup --company "Acme Corp"
```

---

## Core `apply` Command Flow

```
1. Paste or provide job URL / raw text
         ↓
2. Analyzer runs → extracts role, requirements, red flags
         ↓
3. Shows match score + summary → prompts "continue? y/n"
         ↓
4. Tailorer runs → generates tailored resume bullet points
         ↓
5. Cover letter generates → saved to /output/cover_letters/
         ↓
6. Tracker updates → new row added to tracker.xlsx
         ↓
7. Summary printed → "Files saved, good luck!"
```

---

## Application Tracker Columns

| Column | Description |
|---|---|
| Company | Company name |
| Role | Job title |
| Date Applied | Auto-filled on apply |
| Source | Where the listing was found |
| Match Score | 0–100 score from analyzer |
| Status | Applied / Interviewing / Offer / Rejected |
| Follow-up Date | Auto-suggested (2 weeks after apply) |
| Notes | Free text |
| Cover Letter Path | Path to generated file |

---

## LLM Strategy

- **Start with:** Llama 3.1 8B locally via Ollama — free, private, no rate limits
- **Upgrade path:** Ollama Cloud Pro (already subscribed) — same code, just change `base_url`
- **Prompt strategy:** Break complex tasks into smaller focused prompts rather than one large chain to avoid instruction-following issues with 8B models

---

## Known Pitfalls to Plan For

- **Resume PDF parsing** — verify parsed text manually on first run; complex layouts confuse parsers
- **Prompt chaining errors** — analyzer feeds tailorer feeds cover letter; errors compound. Build in a review/confirm step
- **Tracker duplicates** — check for existing Company + Role before inserting a new row
- **Cover letter repetition** — LLMs reuse phrases across letters; add diversity instructions to prompts
- **Instruction following** — Llama 3.1 8B can drop steps in complex prompts; keep each chain focused on one task
