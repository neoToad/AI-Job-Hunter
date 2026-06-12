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
