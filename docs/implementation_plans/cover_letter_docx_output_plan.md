# Cover Letter DOCX Output Plan

## Goal
Replace the plain-text `.txt` cover letter output with an editable `.docx` file that the user can open in Word or Google Docs and customize before submitting.

---

## High-Level Approach

The `generate_cover_letter` chain continues to return plain text (prose is the correct output format for a cover letter). A new utility helper receives that text and writes it into a properly formatted Word document using `python-docx`.

This is a purely mechanical conversion — no LLM prompt changes, no structured JSON, no HTML templates. Paragraphs are split on double newlines; single newlines are preserved as line breaks within a paragraph where appropriate.

---

## Files to Create

| File | Purpose |
|------|---------|
| `job_search_tool/utils/renderers.py` (shared with resume plan) | `render_cover_letter_docx(text: str, path: Path) -> None` — writes the cover letter text into a `.docx` with standard margins and paragraph spacing. |

---

## Files to Modify

| File | Change |
|------|--------|
| `job_search_tool/pipelines.py` | Replace `write_text()` for cover letter with `render_cover_letter_docx(cover_letter, cl_out)` where `cl_out` ends in `.docx`. |
| `job_search_tool/main.py` | Update `apply()` summary panel to reference `.docx` instead of `.txt`. |
| `job_search_tool/app.py` | Change the editable "Cover Letter" text area to a download button for the `.docx` file, or keep the text area as a preview with a download link below it. |
| `job_search_tool/utils/tracker.py` | Remove `"Cover Letter Path"` from `_HEADERS` and drop the `cover_letter_path` parameter from `add_application()`. |
| `job_search_tool/requirements.txt` | Add `python-docx==1.1.2`. |

---

## Rendering Details

```python
def render_cover_letter_docx(text: str, path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    for para in text.split("\n\n"):
        if para.strip():
            p = doc.add_paragraph(para.strip())
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.line_spacing = 1.15

    doc.save(path)
```

- **Date block** (optional enhancement): auto-prepend today's date as a formatted paragraph before the salutation.
- **Font:** Calibri 11pt (Word default), or match a common cover-letter font such as Georgia or Times New Roman.

---

## Tracker Schema Change

The tracker currently stores the cover letter file path in the `"Cover Letter Path"` column. Since the output is now a generated `.docx` that the user is expected to edit externally, storing its original path is no longer useful.

**Action:** Remove `"Cover Letter Path"` from `_HEADERS` in `utils/tracker.py` and remove the `cover_letter_path` parameter from `add_application()`.

**Migration impact:** Existing `.xlsx` files will simply have an extra unused column; openpyxl ignores it. No data migration needed.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| `python-docx` not installed | Add to `requirements.txt`; fallback to `.txt` if import fails. |
| User loses the editable preview in Streamlit | Keep the `st.text_area` as a preview below the download button; the text area reads from `session_state.cover_letter`. |
| Cover letter text contains Markdown (e.g., `**bold**`) from the LLM | Strip simple Markdown syntax in `render_cover_letter_docx` or update the prompt to forbid Markdown. |

---

## Testing Strategy

- Unit test `render_cover_letter_docx`: assert output file exists, has `.docx` extension, and contains expected paragraph text.
- Verify `add_application` no longer accepts or writes a `cover_letter_path`.
- Verify `show_tracker` renders correctly on an old tracker that still contains the orphaned `"Cover Letter Path"` column.
- Integration smoke test: run `apply --dry-run` and assert no `.txt` cover letter file is written.

---

## Acceptance Criteria

- [ ] Running `python main.py apply` produces a `.docx` cover letter instead of `.txt`.
- [ ] The `.docx` opens correctly in Microsoft Word and Google Docs with proper paragraph spacing.
- [ ] No `.txt` cover letter files are created in `output/cover_letters/`.
- [ ] The tracker no longer stores or displays a "Cover Letter Path" column.
- [ ] The Streamlit UI still shows an editable preview of the cover letter text (optional but recommended).
