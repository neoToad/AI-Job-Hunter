# Prompt Customization Guide

The AI behavior in this tool is controlled entirely by plain-text `.txt` files in `job_search_tool/prompts/`. You can edit them with any text editor to change tone, rules, or emphasis — no code changes required.

---

## Prompt File Map

| File | Chain | Purpose |
|------|-------|---------|
| `analyzer_system.txt` | `chains/analyzer.py` | Tells the AI how to score fit and what JSON schema to return |
| `analyzer_human.txt` | `chains/analyzer.py` | Provides the resume and job description to analyze |
| `tailorer_system.txt` | `chains/tailorer.py` | Rules for rewriting resume bullets with ATS keywords |
| `tailorer_human.txt` | `chains/tailorer.py` | Feeds the original resume + target requirements |
| `cover_letter_system.txt` | `chains/cover_letter.py` | Tone, length, and anti-filler rules for cover letters |
| `cover_letter_human.txt` | `chains/cover_letter.py` | Feeds resume + job details + company/role |
| `followup_system.txt` | `chains/followup.py` | Rules for brief, polite follow-up emails |
| `followup_human.txt` | `chains/followup.py` | Feeds company, role, and date applied |

---

## Available Variables

Variables inside `{}` are replaced by the chain at runtime. **Do not rename them.**

| Variable | Available In | Content |
|----------|--------------|---------|
| `{resume}` | `analyzer_human.txt`, `tailorer_human.txt`, `cover_letter_human.txt` | Full text of your parsed resume |
| `{job_description}` | `analyzer_human.txt`, `tailorer_human.txt`, `cover_letter_human.txt` | Full text of the job posting |
| `{company}` | `cover_letter_human.txt` | Company name extracted by the analyzer |
| `{role}` | `cover_letter_human.txt`, `followup_human.txt` | Job title extracted by the analyzer |
| `{must_have}` | `tailorer_human.txt`, `cover_letter_human.txt` | Bullet list of must-have requirements |
| `{matching_skills}` | `tailorer_human.txt`, `cover_letter_human.txt` | Bullet list of skills the candidate has |
| `{date_applied}` | `followup_human.txt` | Date the application was submitted |
| `{format_instructions}` | `analyzer_system.txt` (injected by code) | Pydantic JSON schema instructions |

---

## Tips for Improving Cover Letter Quality

1. **Add industry tone rules**
   If you apply to creative roles (marketing, design), relax the anti-filler rule slightly:
   ```
   Rules:
   - Allow brief enthusiasm if backed by concrete evidence
   - For design roles, mention specific portfolio pieces
   ```

2. **Reference specific achievements**
   If your resume uses quantified outcomes ("increased revenue 30%"), add a rule:
   ```
   - Open paragraphs with quantified outcomes when possible
   ```

3. **Tweak length**
   If you prefer shorter letters, change:
   ```
   - Keep it to 3-4 paragraphs, under 400 words
   ```
   to:
   ```
   - Keep it to 2-3 paragraphs, under 300 words
   ```

---

## Tips for Improving Match Score Accuracy

1. **Adjust the score guidance**
   If the analyzer is too generous or too harsh, edit `analyzer_system.txt`:
   ```json
   "match_score": 0-100,
   ```
   Add context:
   ```
   Scoring guidance:
   - 90-100 = every must-have is clearly evidenced
   - 70-89 = most must-haves match, 1-2 gaps are learnable
   - 50-69 = several gaps, but core skills align
   - 0-49 = major mismatches or unrealistic requirements
   ```

2. **Add red-flag signals**
   If you want to avoid contract-to-hire roles, add:
   ```
   red_flags: ["contract-to-hire", "unpaid trial period", "vague compensation"]
   ```

---

## Common Mistakes When Editing Prompts

### ❌ Renaming a placeholder
```
# BAD — breaks the chain
RESUME:
{my_resume}
```
The chain passes `resume=...`, so `{my_resume}` will not be replaced.

### ❌ Removing `{format_instructions}` from the analyzer
The analyzer chain injects this automatically via `.partial()`. You don't need to write it in `analyzer_human.txt`, but if you accidentally put literal JSON schema instructions there and remove the reference, the model may produce malformed JSON.

### ❌ Making system prompts too vague
```
# BAD
You are a helpful assistant. Do the task.
```
Specific, numbered rules produce far more consistent output than generic instructions.

### ✅ Good example
```
Rules:
1. Never invent experience the candidate does not have
2. Keep the same meaning, just improve keyword alignment
3. Use strong action verbs
4. Be specific and quantify where the original resume does
5. Return the full rewritten resume text, preserving all sections and headings
```

---

## Reloading Prompts

There is no caching layer — edits take effect **immediately** the next time you run a command. No restart required.
