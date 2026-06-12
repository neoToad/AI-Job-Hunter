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
