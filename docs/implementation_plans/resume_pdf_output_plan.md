# Resume PDF Output Plan

## Goal
Replace the plain-text `.txt` tailored resume output with a professionally formatted `.pdf` that preserves the visual structure of the original resume.

---

## High-Level Approach

Instead of rewriting the resume as a single text blob, the tailorer chain will return **structured JSON** representing resume sections (contact info, summary, experience, education, skills). A Jinja2 HTML template will render that JSON into a styled resume, and a headless browser engine will convert the HTML to PDF.

This avoids brittle in-place PDF text replacement (which breaks on font sizing, overflow, and multi-column layouts).

---

## Files to Create

| File | Purpose |
|------|---------|
| `job_search_tool/templates/resume.html` | Jinja2 template with standard resume layout (contact header, experience blocks, skills, education). CSS handles fonts, spacing, and page breaks. |
| `job_search_tool/utils/renderers.py` | `render_resume_pdf(structured_resume: dict, path: Path) -> None` — renders the dict through `resume.html` via Jinja2, then converts HTML → PDF with pdfkit. |

---

## Files to Modify

| File | Change |
|------|--------|
| `job_search_tool/chains/tailorer.py` | Replace plain-text return with structured JSON. Add a `TailoredResume` Pydantic model (contact, summary, experience[], education[], skills[]). Use `JsonOutputParser` + `OutputParserException` wrapping identical to `analyzer.py`. |
| `job_search_tool/chains/prompts/tailorer_system.txt` | Update instructions: "Return valid JSON with keys: contact, summary, experience, education, skills. Do not return Markdown or plain text." |
| `job_search_tool/pipelines.py` | Replace `write_text()` for resume with `render_resume_pdf(tailored_resume_dict, resume_out)` where `resume_out` ends in `.pdf`. |
| `job_search_tool/main.py` | Update `apply()` summary panel to reference `.pdf` instead of `.txt`. |
| `job_search_tool/app.py` | Remove or re-label the editable "Tailored Resume" text area; the user downloads a PDF, not edits text. Optionally keep a preview. |
| `job_search_tool/requirements.txt` | Add `Jinja2`, `pdfkit`, and install `wkhtmltopdf` binary (not pip; see Dependencies). |

---

## Data Model: `TailoredResume`

```python
class ExperienceEntry(BaseModel):
    title: str
    company: str
    dates: str
    bullets: list[str]

class TailoredResume(BaseModel):
    contact: dict[str, str]          # name, email, phone, location, linkedin
    summary: str
    experience: list[ExperienceEntry]
    education: list[dict[str, str]]  # degree, school, dates
    skills: list[str]
```

The LLM receives the original resume text, job description, and `must_have`/`matching_skills` as context. It returns JSON conforming to this schema.

---

## Rendering Pipeline

```
structured dict ──► Jinja2 (resume.html) ──► HTML string ──► pdfkit ──► .pdf file on disk
```

`pdfkit` requires the `wkhtmltopdf` binary installed on the host. On Windows the binary ships as an installer; on Ubuntu it is `apt-get install wkhtmltopdf`. The `pdfkit` Python wrapper locates it via `PATH` or an explicit config path.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM returns malformed JSON | Wrap in `JsonOutputParser`; catch `OutputParserException` and raise `ValueError` with a friendly retry message. |
| `wkhtmltopdf` not installed on user's machine | Document prerequisite in README; add graceful fallback in `render_resume_pdf` that writes `.txt` if the binary is missing. |
| HTML template is too opinionated (single-column vs two-column) | Start with a single clean layout. Future iterations can offer multiple templates. |
| CI runners lack `wkhtmltopdf` | Add install step in `.github/workflows/test.yml`; skip PDF rendering tests if the binary is absent. |

---

## Testing Strategy

- Unit test `render_resume_pdf` with a dummy dict: assert the output file exists and has `.pdf` extension.
- Mock `pdfkit.from_string` to avoid requiring the binary in unit tests.
- Unit test `tailor_resume` with `FakeListChatModel` returning valid JSON; assert the returned dict has expected keys.
- Integration smoke test: run `apply --dry-run` and assert no `.txt` resume file is written.

---

## Acceptance Criteria

- [ ] Running `python main.py apply` produces a `.pdf` tailored resume instead of `.txt`.
- [ ] The PDF contains the candidate's contact info, rewritten experience bullets, education, and skills.
- [ ] No `.txt` resume files are created in `output/tailored_resumes/`.
- [ ] If `wkhtmltopdf` is missing, the tool degrades gracefully (falls back to `.txt` or shows a clear error).
- [ ] Existing tracker entries are unaffected by the removed `.txt` resume (tracker never stored resume path anyway).
