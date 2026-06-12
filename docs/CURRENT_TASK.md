# Current Task

## Prompt 19 — Best Practices: Tracker Robustness

**What I'm actively working on:**
Improving `utils/tracker.py`:
1. Validate `company` and `role` are non-empty strings in `add_application()` — raise ValueError if empty.
2. Handle empty rows in `show_tracker()` — print "No applications found."
3. Handle corrupt/unexpected date formats in `get_followups_due()` — skip unparseable dates rather than crashing.
4. Add `update_status(path, company, role, new_status)` function with valid statuses: Applied, Interviewing, Offer, Rejected, Withdrawn.
5. Expose `update_status` as new CLI command in `main.py`:
   `python main.py status --company "Acme" --role "Engineer" --status "Interviewing"`

**Next step:** Commit Prompt 19, then move to Prompt 20.
