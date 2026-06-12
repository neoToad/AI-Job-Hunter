# AI Job Hunter

A command-line assistant that helps you analyze job postings, tailor your resume,
generate cover letters, and track applications — all backed by a local (or cloud)
LLM via Ollama. Also includes a Streamlit UI for the most copy-paste-heavy workflows.

---

## Prerequisites

- **Python 3.11+**
- **Ollama** installed locally (or an Ollama Cloud Pro account)
- **Git** (to clone the repo)

---

## Setup

1. **Clone the repository** (if you haven't already).

2. **Install dependencies:**
   ```bash
   pip install -r job_search_tool/requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cd job_search_tool
   cp .env.example .env
   ```
   Edit `.env` to set your paths and model preferences.

4. **Place your resume:**
   - Put a PDF named `resume.pdf` inside `job_search_tool/resume/` (or update `RESUME_PATH` in `.env`).

---

## Running Ollama Locally

1. **Install Ollama** from [ollama.com](https://ollama.com).

2. **Pull the default model:**
   ```bash
   ollama pull llama3.1
   ```

3. **Start the server:**
   ```bash
   ollama serve
   ```

The CLI will connect to `http://localhost:11434` by default.

---

## Switching to Ollama Cloud Pro

If you prefer a managed endpoint, update `.env`:

```bash
OLLAMA_BASE_URL=https://api.ollama.cloud
OLLAMA_API_KEY=your_api_key_here
OLLAMA_MODEL=llama3.1
```

---

## CLI Commands

All commands are run from the `job_search_tool/` directory:

### `verify`
Check that your resume is parseable and Ollama is reachable with the configured model available.

```bash
python main.py verify
```

Expected output:
```
Resume OK — John Doe | Python Developer | 5 years...
Ollama OK — model llama3.1 is available.
```

---

### `analyze`
Get a structured analysis with match score, matching/missing skills, red flags, and a recommendation.

**Paste from stdin:**
```bash
python main.py analyze
# Paste the job description, then press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done.
```

**Read from a file:**
```bash
python main.py analyze --file path/to/job.txt
```

**Fetch from a URL:**
```bash
python main.py analyze --url https://example.com/job-posting
```

---

### `apply`
Run the full application pipeline:
1. Parse your resume.
2. Analyze fit.
3. Optionally tailor your resume.
4. Generate a cover letter.
5. Save both to `output/`.
6. Log the application in `data/tracker.xlsx`.

**Paste from stdin:**
```bash
python main.py apply
```

**Read from a file:**
```bash
python main.py apply --file path/to/job.txt
```

**Fetch from a URL:**
```bash
python main.py apply --url https://example.com/job-posting
```

Skip resume tailoring:
```bash
python main.py apply --skip-tailor
```

Dry-run (analyze only, no files saved):
```bash
python main.py apply --dry-run
```

---

### `status`
Update the status of an existing application in the tracker.

```bash
python main.py status --company "Acme Corp" --role "Software Engineer" --status "Interviewing"
```

Valid statuses: `Applied`, `Interviewing`, `Offer`, `Rejected`, `Withdrawn`.

---

### `followup`
Draft a polite follow-up email.

**Pick from due follow-ups in the tracker:**
```bash
python main.py followup
```

**Draft for a specific application:**
```bash
python main.py followup --company "Acme Corp" --role "Software Engineer" --date "2026-06-01"
```

---

### `tracker`
Display the full application tracker as a formatted table.

```bash
python main.py tracker --show
```

**Delete an entry:**
```bash
python main.py tracker --delete --company "Acme Corp" --role "Software Engineer"
```
You will be asked to confirm before the row is removed.

**Edit a field:**
```bash
python main.py tracker --edit --company "Acme Corp" --role "Software Engineer" --field "Notes" --value "Had phone screen"
```

Valid editable fields: `Source`, `Match Score`, `Status`, `Follow-up Date`, `Notes`, `Cover Letter Path`.

---

## Streamlit UI

For a web interface (great for copy-pasting long job descriptions), run:

```bash
streamlit run app.py
```

Then open your browser to the URL printed in the terminal (usually `http://localhost:8501`).

The UI has two modes:
- **Analyze Job** — paste a description and see the structured analysis instantly.
- **Full Application** — run the entire pipeline with a progress bar, then edit the generated cover letter and tailored resume before they are saved.

---

## Customizing Prompts

All AI behavior is controlled by plain-text files in `job_search_tool/prompts/`:

| File | Controls |
|------|----------|
| `analyzer_system.txt` | How the analyzer scores fit and structures JSON |
| `analyzer_human.txt` | Resume + job description layout sent to the analyzer |
| `tailorer_system.txt` | Rules for rewriting resume bullets |
| `tailorer_human.txt` | Original resume + requirements sent to the tailorer |
| `cover_letter_system.txt` | Tone and structure rules for cover letters |
| `cover_letter_human.txt` | Resume + job details sent to the cover letter chain |
| `followup_system.txt` | Tone and length rules for follow-up emails |
| `followup_human.txt` | Application details sent to the follow-up chain |

**Never rename the `{placeholder}` variables** inside these files — they must match the keys passed by the chain code. See `docs/prompt_guide.md` for a full variable map and tips.

---

## Project Structure

```
job_search_tool/
├── main.py                  # Typer CLI entry point
├── app.py                   # Streamlit UI
├── config.py                # Environment & path configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment file
├── prompts/                 # AI prompt templates (.txt files)
├── resume/                  # Your resume.pdf
├── data/                    # tracker.xlsx
├── output/
│   ├── cover_letters/
│   └── tailored_resumes/
├── chains/
│   ├── llm.py               # LLM factory
│   ├── analyzer.py          # Job analysis chain
│   ├── tailorer.py          # Resume tailoring chain
│   ├── cover_letter.py      # Cover letter chain
│   └── followup.py          # Follow-up email chain
└── utils/
    ├── resume_parser.py     # PDF text extraction
    ├── tracker.py           # Excel application tracker
    └── helpers.py           # Shared helpers (slug generation)
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Cannot reach Ollama` | `ollama serve` is not running | Start it with `ollama serve` |
| `Resume not found` | PDF is not at `resume/resume.pdf` | Move it there or update `RESUME_PATH` in `.env` |
| `Could not parse resume` | PDF is image-based (scanned) | Re-save as a text-based PDF or use OCR first |
| `AI returned unexpected format` | LLM output is not valid JSON | Re-run `analyze`; check `prompts/analyzer_system.txt` has the schema example |
| `PermissionError` on tracker | `tracker.xlsx` is open in Excel | Close the file and retry |
| URL fetch returns <200 characters | Page is loaded by JavaScript | Use `--file` with manually copied text instead |
| Streamlit won't start | `streamlit` not installed or port 8501 in use | Run `pip install streamlit` or specify `--server.port 8502` |

For more detail, see `docs/troubleshooting.md`.

---

## Notes

- The tracker is an `.xlsx` file managed with `openpyxl`. It is created automatically on first use.
- Output filenames are auto-generated as safe slugs: `company_role_YYYY-MM-DD.txt`.
- All LLM calls use `SpinnerColumn` progress indicators so the UI stays responsive.
