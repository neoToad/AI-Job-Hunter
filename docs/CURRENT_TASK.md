# Current Task

## Step 4: Add Windows reserved name check to `make_slug`

**Status:** In progress

**What I'm doing:**
- In `job_search_tool/utils/helpers.py`, review `sanitize_filename` (which `make_slug` relies on).
- `sanitize_filename` already checks Windows reserved names, but truncation can leave trailing dots/spaces. Adding a second strip after truncation ensures `make_slug` never produces filenames ending in `.` or ` `.

**Next step:** Commit and push, then move to Step 5 (Validate `--file` path is actually a file).
