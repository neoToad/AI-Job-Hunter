# Changelog

## [Unreleased]

Branch: `feature/job-search-round-3`

---

### [Prompt 21] Overwrite all 8 prompt files with exact spec content

**What was built:**
Replaced all 8 `prompts/*.txt` files with the exact content from the spec:
- `analyzer_system.txt` — now includes full JSON schema example and explicit instructions to be honest/realistic
- `analyzer_human.txt` — simplified to only `{resume}` and `{job_description}` placeholders
- `tailorer_system.txt` — now explicitly mentions ATS optimization and stronger rules
- `tailorer_human.txt` — restructured with clear section headers
- `cover_letter_system.txt` — added stronger anti-filler rules and human tone requirement
- `cover_letter_human.txt` — added `COMPANY` and `ROLE` fields
- `followup_system.txt` — added "do not grovel" rule
- `followup_human.txt` — now a full sentence with placeholders

**Refactors/improvements:**
- Verified all placeholder names match the keys passed to `chain.invoke()` in each chain module

**Deviations:**
- None

---

### [Prompt 22] Add file and URL input for CLI analyze and apply commands

**What was built:**
Replaced the old "paste until END" input with a proper `--file` / `--url` / stdin helper in `main.py`:
- `get_job_description(file, url) -> str` handles all three input modes
- `--file` reads plain text from a file path
- `--url` fetches the page with requests, parses with BeautifulSoup (lxml), strips script/style/nav/header/footer, deduplicates blank lines, and warns if extracted text is < 200 characters
- Default stdin mode now prints a cleaner prompt mentioning Ctrl+D / Ctrl+Z instead of "type END"
- Added `beautifulsoup4` and `lxml` to `requirements.txt`

**Refactors/improvements:**
- URL fetch has a 10-second timeout and validates the scheme (http:// or https://)
- Uses `handle_error()` for consistent error messages on file/URL failures

**Deviations:**
- None

---

### [Prompt 23] Add tracker delete and edit subcommands

**What was built:**
Added CRUD operations to the application tracker:
- `delete_application(path, company, role)` in `utils/tracker.py` — finds row by company+role (case-insensitive), deletes it, saves workbook
- `edit_application(path, company, role, field, value)` in `utils/tracker.py` — finds row, updates the specified column, saves workbook
- `tracker --delete --company "X" --role "Y"` in `main.py` — asks for y/n confirmation before deleting
- `tracker --edit --company "X" --role "Y" --field "Notes" --value "Z"` in `main.py` — prints confirmation of what was changed
- Valid editable fields: Source, Match Score, Status, Follow-up Date, Notes, Cover Letter Path

**Refactors/improvements:**
- Reused existing `application_exists()` for pre-delete existence check so the confirmation prompt happens before any mutation
- Added clear error hints when required flags are missing for --delete or --edit

**Deviations:**
- None

---

### [Prompt 24] Add Streamlit UI with Analyze and Full Application modes

**What was built:**
Created `app.py` providing a web UI for the two most copy-paste-heavy commands:
- Sidebar with mode radio buttons ("Analyze Job" / "Full Application") and Job Source input
- Analyze mode: calls `parse_resume` + `analyze_job`, displays match score metric, recommendation badge (success/warning/error), and organized expanders for must-have, matching skills, missing skills, red flags, nice-to-have
- Full Application mode: runs full pipeline with `st.progress()` bar, shows editable cover letter and tailored resume in `st.text_area` widgets
- Dry run checkbox in Full Application mode only runs analysis with an info banner
- Duplicate detection shows a warning and requires a confirmation checkbox before proceeding
- Added `streamlit` to `requirements.txt`

**Refactors/improvements:**
- Used `@st.cache_resource` for resume parsing so it only runs once per Streamlit session
- All logic imported directly from `chains/` and `utils/` — zero duplication of business logic

**Deviations:**
- None

---

### [Prompts 25–27] Audit Plans (Refactor, Best Practices, Testing)

**What was built:**
Three markdown audit plans with no code changes:
- `docs/refactor_plan.md` — duplicated `_load_prompt`, progress spinner blocks, resume parse blocks; long functions (`apply`, `tracker`); inconsistent `load_workbook` modes; Streamlit/CLI overlap; prioritized by impact vs effort
- `docs/best_practices_plan.md` — type hints (minor `Any` tightening), missing docstring on `first_run_check`, unprotected `wb.save()` in tracker, path traversal risk in `--file`, missing `st.session_state` in app.py, LangChain temperatures appropriate, LCEL used everywhere
- `docs/testing_plan.md` — test cases per file, mock strategy (FakeListChatModel, tmp_path), conftest fixtures, CI workflow, coverage targets, prioritized by risk

**Refactors/improvements:**
- None (plan-only prompts)

**Deviations:**
- None

---

### [Prompt 28] Add documentation plan and implement all docs

**What was built:**
Phase 1 — produced `docs/documentation_plan.md` identifying gaps in README, user guide, prompt guide, and troubleshooting.

Phase 2 — implemented all documentation:
- Updated `README.md`: added Python 3.11+ prerequisite, Streamlit UI section, `--file`/`--url` examples for analyze/apply, `tracker --delete`/`--edit` examples, updated project structure with `prompts/` and `app.py`, troubleshooting quick-reference table
- Created `docs/user_guide.md`: daily workflow (find → analyze → apply → track → status → follow up), interpreting match scores (≥70 apply, 50–69 stretch, <50 skip), ASCII mockups of CLI output, Streamlit UI walkthrough, productivity tips
- Created `docs/prompt_guide.md`: prompt file map per chain, available variables table (`{resume}`, `{job_description}`, `{company}`, `{role}`, `{must_have}`, `{matching_skills}`, `{date_applied}`), tips for improving cover letter quality and match score accuracy, common mistakes when editing prompts (renaming placeholders, removing format instructions, vague system prompts)
- Created `docs/troubleshooting.md`: Ollama not reachable, resume PDF won't parse, LLM malformed JSON, tracker file locked, URL fetch fails/empty content, Streamlit won't start

**Refactors/improvements:**
- README now accurately reflects the current implementation instead of the legacy "type END" behavior

**Deviations:**
- None

---

### [Prompt 29] Performance audit plan and Low/Medium improvements

**What was built:**
Phase 1 — produced `docs/performance_plan.md` identifying parallelizable LLM calls, redundant resume parsing, URL re-fetching, missing `st.session_state`, and lazy-import opportunity.

Phase 2 — implemented all Low/Medium improvements:
- `utils/resume_parser.py`: added `get_resume_text()` with disk cache (`resume/resume_cache.txt`) keyed by PDF mtime; `preview_resume` now uses it so `verify` benefits too
- `utils/helpers.py`: added `fetch_url_text()` with JSON cache in `data/url_cache.json`, 24-hour expiry; deduplicates BeautifulSoup logic that was previously only in `main.py`
- `main.py`: replaced inline URL fetch with `fetch_url_text`, replaced `parse_resume` with `get_resume_text`, added `asyncio.to_thread()` parallelization for `tailor_resume` + `generate_cover_letter` in `apply()`, lazy-imported chain modules inside commands to speed up cold starts for non-LLM commands
- `app.py`: replaced `parse_resume` with `get_resume_text`, added `asyncio.to_thread()` parallelization for tailor + cover letter, added `st.session_state` with stale-state clearing so analysis results and generated outputs persist across Streamlit reruns

**Refactors/improvements:**
- `get_resume_text` gracefully ignores cache write failures (best-effort caching)
- `fetch_url_text` gracefully ignores cache read/write failures

**Deviations:**
- None

---
