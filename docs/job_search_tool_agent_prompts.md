# Job Search CLI Tool — Agent Handoff Prompts

## How to Use
Run these prompts sequentially in your CLI agent (e.g. Claude Code).
Each prompt is self-contained and builds on the previous step.

---

## Prompt 1 — Project Scaffold

```
Create a Python CLI project called `job_search_tool` with the following structure:

job_search_tool/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── resume/          (empty, for user's resume.pdf)
├── data/            (empty, for tracker.xlsx)
├── output/
│   ├── cover_letters/
│   └── tailored_resumes/
├── chains/
│   ├── __init__.py
│   ├── llm.py
│   ├── analyzer.py
│   ├── tailorer.py
│   ├── cover_letter.py
│   └── followup.py
└── utils/
    ├── __init__.py
    ├── resume_parser.py
    └── tracker.py

Requirements.txt should include:
langchain, langchain-ollama, langchain-community, pdfplumber, openpyxl, typer[all], rich, python-dotenv, pydantic, requests

.env.example should include:
- OLLAMA_BASE_URL (default http://localhost:11434, with a comment showing Ollama Cloud Pro URL)
- OLLAMA_MODEL (default llama3.1)
- RESUME_PATH (default resume/resume.pdf)
- TRACKER_PATH (default data/tracker.xlsx)
- OUTPUT_DIR (default output)

config.py should load all values from .env using python-dotenv and define Path constants for all file locations. It should also ensure output directories are created on import.
```

---

## Prompt 2 — LLM Setup

```
In `chains/llm.py`, create a `get_llm()` function that returns a configured ChatOllama instance using the OLLAMA_BASE_URL and OLLAMA_MODEL values from config.py. Accept a `temperature` float parameter defaulting to 0.3.

This single function will be imported by all other chain files so that swapping models only requires changing one place.
```

---

## Prompt 3 — Resume Parser

```
In `utils/resume_parser.py`, implement two functions using pdfplumber:

1. `parse_resume(path: Path) -> str`
   - Extract all text from a PDF resume
   - Join pages with double newlines
   - Raise FileNotFoundError if the file doesn't exist
   - Print a rich warning if any page returns no text (may be image-based)
   - Raise ValueError if no text is extracted at all

2. `preview_resume(path: Path, chars: int = 500) -> str`
   - Return a short preview of the parsed text for verification purposes
```

---

## Prompt 4 — Application Tracker

```
In `utils/tracker.py`, implement a spreadsheet tracker using openpyxl with these columns:
Company, Role, Date Applied, Source, Match Score, Status, Follow-up Date, Notes, Cover Letter Path

Implement these functions:

1. `_get_or_create_workbook(path)` — load or create the workbook with bold headers
2. `application_exists(path, company, role) -> bool` — check for duplicate company+role (case-insensitive)
3. `add_application(path, company, role, source, match_score, notes, cover_letter_path)` — append a new row. Auto-fill Date Applied as today, Status as "Applied", Follow-up Date as 2 weeks from today.
4. `show_tracker(path)` — print all rows as a formatted Rich table
5. `get_followups_due(path) -> list[dict]` — return applications where Status is "Applied" and Follow-up Date is today or earlier
```

---

## Prompt 5 — Job Analyzer Chain

```
In `chains/analyzer.py`, create a LangChain chain that analyzes a job description against a resume.

Create a Pydantic model `JobAnalysis` with these fields:
- company: str
- role: str  
- must_have: list[str]
- nice_to_have: list[str]
- red_flags: list[str]
- match_score: int (0-100)
- matching_skills: list[str]
- missing_skills: list[str]
- recommendation: Literal["apply", "skip", "stretch"]
- summary: str

Create a `analyze_job(resume: str, job_description: str) -> JobAnalysis` function using:
- A ChatPromptTemplate that instructs the LLM to respond ONLY in valid JSON matching the JobAnalysis structure
- JsonOutputParser with the Pydantic model
- Temperature 0.1 (low, for consistent structured output)
- The prompt should instruct the model to be honest and never invent skills the candidate doesn't have
```

---

## Prompt 6 — Resume Tailorer Chain

```
In `chains/tailorer.py`, create a `tailor_resume(resume: str, job_description: str, analysis: JobAnalysis) -> str` function.

Use a ChatPromptTemplate that:
- Takes the original resume, job description, must-have requirements, and matching skills as inputs
- Instructs the LLM to rewrite resume bullet points using keywords from the job posting
- Explicitly forbids inventing experience the candidate doesn't have
- Tells the model to preserve all resume sections and use strong action verbs
- Use temperature 0.2
- Return plain string output via StrOutputParser
```

---

## Prompt 7 — Cover Letter Chain

```
In `chains/cover_letter.py`, create a `generate_cover_letter(resume: str, job_description: str, analysis: JobAnalysis) -> str` function.

Use a ChatPromptTemplate that:
- Takes resume, job description, company, role, must-have requirements, and matching skills as inputs
- Instructs the LLM to write a 3-4 paragraph cover letter under 400 words
- Explicitly forbids generic filler phrases like "I am excited to apply" or "I am a team player"
- Instructs the model to map specific resume evidence to specific job requirements
- Use temperature 0.5 for more natural writing
- Return plain string output via StrOutputParser
```

---

## Prompt 8 — Follow-up Email Chain

```
In `chains/followup.py`, create a `draft_followup(company: str, role: str, date_applied: str) -> str` function.

Use a ChatPromptTemplate that:
- Takes company, role, and date_applied as inputs
- Instructs the LLM to write a polite follow-up email under 100 words
- Explicitly says not to be pushy or grovel
- Should reference the specific role and ask politely about the timeline
- Use temperature 0.4
- Return plain string output via StrOutputParser
```

---

## Prompt 9 — CLI Entry Point

```
In `main.py`, build a Typer CLI app with Rich output. Implement these commands:

1. `verify` — check that the resume PDF is parseable and Ollama is reachable. Hit the Ollama /api/tags endpoint and confirm the configured model is available.

2. `analyze` — parse the resume, prompt the user to paste a job description (read lines until user enters "END" on a blank line), run analyze_job(), and display the results with Rich formatting: match score in color (green ≥70, yellow ≥50, red <50), matching skills in green with checkmarks, missing skills in red with X marks, red flags in yellow with warning symbols.

3. `apply` — full pipeline in sequence:
   - Parse resume
   - Collect job description (same END-terminated paste method)
   - Run analyzer and display summary
   - Ask "Continue with this application? y/n"
   - Check for duplicates in tracker, warn if found
   - Tailor resume (skippable with --skip-tailor flag)
   - Generate cover letter
   - Save both to /output/ with a slug filename: {company}_{role}_{date}.txt
   - Prompt for optional notes
   - Update tracker
   - Print a summary panel with file paths

4. `followup` — accepts --company, --role, --date options. If no company given, load follow-ups due from tracker and let user pick by number. Draft and display the email, offer to save it to a file.

5. `tracker --show` — display the full tracker as a Rich table.

Use SpinnerColumn progress indicators during all LLM calls.
```

---

## Prompt 10 — Wiring & Testing

```
Review all files in the job_search_tool project for the following:

1. All imports are correct and consistent (e.g. config is imported as a module, paths use pathlib.Path)
2. Every chain file imports get_llm from chains.llm
3. The tracker correctly handles the case where tracker.xlsx does not yet exist
4. main.py handles exceptions gracefully — if resume parsing fails or Ollama is unreachable, print a helpful error message and exit cleanly rather than showing a Python traceback
5. The output directory slug uses a helper that makes filenames safe (lowercase, spaces to underscores, slashes to dashes)

Fix any issues found. Then write a README.md with:
- Setup instructions (clone, pip install -r requirements.txt, copy .env.example to .env, place resume.pdf)
- How to run ollama locally (ollama pull llama3.1, ollama serve)
- How to switch to Ollama Cloud Pro (change OLLAMA_BASE_URL in .env)
- All CLI commands with example usage
```
