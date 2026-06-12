# Job Search CLI Tool

A command-line assistant that helps you analyze job postings, tailor your resume,
generate cover letters, and track applications — all backed by a local (or cloud)
LLM via Ollama.

---

## Setup

1. **Clone the repository** (if you haven't already).

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to set your paths and model preferences.

4. **Place your resume:**
   - Put a PDF named `resume.pdf` inside the `resume/` folder (or update `RESUME_PATH` in `.env`).

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

### `verify`
Check that your resume is parseable and Ollama is reachable with the configured model available.

```bash
python main.py verify
```

---

### `analyze`
Paste a job description and get a structured analysis with match score, matching/missing skills, red flags, and a recommendation.

```bash
python main.py analyze
# Paste the job description, then type END on its own line.
```

---

### `apply`
Run the full application pipeline:
1. Parse your resume.
2. Paste the job description.
3. Analyze fit.
4. Optionally tailor your resume.
5. Generate a cover letter.
6. Save both to `output/`.
7. Log the application in `data/tracker.xlsx`.

```bash
python main.py apply
```

Skip resume tailoring:
```bash
python main.py apply --skip-tailor
```

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

---

## Project Structure

```
job_search_tool/
├── main.py                  # Typer CLI entry point
├── config.py                # Environment & path configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment file
├── README.md                # This file
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

## Notes

- The tracker is an `.xlsx` file managed with `openpyxl`. It is created automatically on first use.
- Output filenames are auto-generated as safe slugs: `company_role_YYYY-MM-DD.txt`.
- All LLM calls use `SpinnerColumn` progress indicators so the UI stays responsive.
