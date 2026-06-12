# Job Search CLI Tool — Prompts 28–30 (Documentation, Performance & Security)

## How to Use
Run these after Prompts 25–27 and their implementation plans have been executed.
Prompts 28 and 29 follow the same scan-first, plan-then-implement pattern.
Prompt 30 is safe to implement directly — no plan phase needed.

---

## Prompt 28 — Documentation

### Phase 1: Scan & Plan
```
Scan every file in the job_search_tool project and produce a documentation plan.
Do NOT make any changes yet. Output only a markdown file saved to:
docs/documentation_plan.md

The plan should identify:

1. README GAPS
   - Check the existing README.md covers:
     - Prerequisites (Python version, Ollama install, model pull)
     - Setup steps in exact order (clone, pip install, .env, resume placement)
     - Every CLI command with a real example and expected output
     - How to switch between local Ollama and Ollama Cloud Pro
     - How to run the Streamlit UI (streamlit run app.py)
     - How to edit prompt .txt files to customize AI behavior
     - Troubleshooting section (Ollama not running, PDF won't parse, JSON errors)
   - List every gap found

2. USER GUIDE
   - Outline a docs/user_guide.md covering:
     - A typical daily workflow (find job → apply → track → follow up)
     - Screenshots or ASCII mockups of expected CLI output for each command
     - How to interpret match scores and recommendations
     - How to customize prompts for your writing style

3. PROMPT CUSTOMIZATION GUIDE
   - Outline a docs/prompt_guide.md explaining:
     - What each prompt file in prompts/ controls
     - What variables are available in each prompt ({resume}, {job_description}, etc.)
     - Tips for improving cover letter quality
     - Tips for improving match score accuracy
     - Common mistakes when editing prompts (breaking variable names, etc.)

4. TROUBLESHOOTING GUIDE
   - Outline a docs/troubleshooting.md covering the most likely failure modes:
     - Ollama not reachable
     - Resume PDF won't parse
     - LLM returns malformed JSON
     - Tracker file is locked (open in Excel)
     - URL fetch fails or returns empty content
     - Streamlit won't start

For each section, note: exists / missing / needs update.
At the end, list all docs files to be created or updated with their full outline.
```

### Phase 2: Implement
```
Using the plan in docs/documentation_plan.md, implement all documentation changes:

1. Update README.md to fill all identified gaps
2. Create docs/user_guide.md with the full user workflow
3. Create docs/prompt_guide.md explaining how to customize each prompt file
4. Create docs/troubleshooting.md with all identified failure modes and fixes

For the user guide, use ASCII representations of terminal output rather than
screenshots since this is a text-based tool. For example:

  $ python main.py analyze --url https://example.com/job

  ┌─────────────────────────────────┐
  │ Job Description Analyzer        │
  └─────────────────────────────────┘

  Acme Corp — Senior Python Engineer
  Match Score: 82/100
  Recommendation: APPLY
  ...

Make all docs accurate to the actual current implementation — read the source
files before writing, do not assume behavior.
```

---

## Prompt 29 — Performance Audit

### Phase 1: Scan & Plan
```
Scan every file in the job_search_tool project and produce a performance plan.
Do NOT make any changes yet. Output only a markdown file saved to:
docs/performance_plan.md

The plan should identify:

1. SEQUENTIAL LLM CALLS THAT COULD BE PARALLELIZED
   - Map out every LLM call in the apply pipeline and draw the dependency graph:
     - Which calls depend on the output of a previous call?
     - Which calls are independent and could run concurrently?
   - Specifically assess whether resume tailoring and cover letter generation
     could run in parallel using asyncio since both only need the analyzer output
   - Estimate time saved per application run

2. REDUNDANT WORK
   - The resume is re-parsed from PDF on every single command invocation
     Assess whether it should be parsed once and cached (e.g. as resume_cache.txt)
     and only re-parsed if the PDF modification date has changed
   - The job description is re-processed from scratch even if the same URL
     is fetched twice. Assess a simple URL → text cache using a JSON file

3. LLM CALL OPTIMIZATION
   - Review all prompt templates and identify any that send more tokens than needed
     (e.g. sending the full resume when only skills section is relevant)
   - Assess whether a two-stage approach would be faster for matching:
     Stage 1: cheap/fast call to score and filter (use a smaller model or shorter prompt)
     Stage 2: full calls only for jobs that pass the threshold
   - Identify any prompt that is likely to produce long outputs that could be
     constrained with a max length instruction to reduce token usage

4. STREAMLIT PERFORMANCE
   - Identify any expensive operation in app.py that runs on every Streamlit rerun
     (Streamlit reruns the entire script on every interaction)
   - Assess what should be wrapped in @st.cache_data or @st.cache_resource
   - Specifically: resume parsing should only happen once per session, not on
     every button click

5. STARTUP TIME
   - Identify any imports that are slow or should be lazy-loaded
   - Check if all chain imports at the top of main.py are needed for every command
     or could be imported only when the relevant command runs

For each finding include:
- Where the issue is (file + function)
- What the performance impact is (estimated)
- What the fix is
- Complexity: Low / Medium / High

At the end, produce a prioritized list ordered by estimated time saved per use.
```

### Phase 2: Implement
```
Using the plan in docs/performance_plan.md, implement all Low and Medium complexity
improvements. Skip any marked High complexity unless they appear in the top 3
by estimated impact.

Specifically make sure to:
1. Add @st.cache_resource for resume parsing in app.py so it only runs once per session
2. Add a resume text cache (resume/resume_cache.txt) that is invalidated when
   the PDF modification date changes — implement in utils/resume_parser.py
3. Add asyncio parallelization for tailoring and cover letter generation if identified
   as independent in the plan — implement in main.py and app.py apply flows
4. Add a simple URL cache (data/url_cache.json) that stores fetched job description
   text keyed by URL with a timestamp, expiring after 24 hours

Do not implement anything not in the approved plan.
After implementing, run python main.py verify to confirm nothing is broken.
```

---

## Prompt 30 — Secrets & .gitignore Audit (Implement Directly)

```
Perform a security and secrets audit on the job_search_tool project and fix all
issues found. This prompt implements fixes directly — no plan phase needed.

1. .gitignore
   Create or update .gitignore to ensure the following are never committed to git:

   # Environment
   .env

   # Personal data
   resume/
   data/
   output/

   # Python
   __pycache__/
   *.pyc
   *.pyo
   .venv/
   venv/
   *.egg-info/
   dist/
   build/

   # Streamlit
   .streamlit/secrets.toml

   # OS
   .DS_Store
   Thumbs.db

   # Docs build artifacts
   docs/*.pdf

2. HARDCODED VALUES SCAN
   Search every Python file for:
   - Any string that looks like an API key, token, or password
   - Any hardcoded file path that uses a username or home directory (e.g. /Users/john/)
   - Any hardcoded URL that should be in config (besides the Ollama default)
   - Any os.getenv() call outside of config.py
   
   Fix all findings by moving values to config.py and .env.example

3. PATH TRAVERSAL PROTECTION
   In utils/tracker.py and anywhere filenames are built from user input
   (company name, role name), add a sanitize_filename() helper that:
   - Strips any path separators (/ \ ..)
   - Removes characters not safe for filenames: < > : " | ? * and control chars
   - Truncates to 50 characters
   - Falls back to "unknown" if the result is empty after sanitization
   
   Apply this helper everywhere a user-supplied string is used in a file path
   (the slug helper in main.py, cover letter path, tailored resume path)

4. URL FETCH SAFETY
   In the URL fetching code added in Prompt 22, verify:
   - requests.get() has a timeout parameter (use 10 seconds)
   - Only http:// and https:// URLs are accepted — reject others with a clear error
   - The fetched content length is capped before passing to the LLM
     (truncate at 8000 characters to avoid massive token usage on bloated pages)

5. RESUME CONTENT IN ERRORS
   Verify that no exception handler or error message prints the full resume text
   or job description text to the terminal. If any do, replace with a short
   placeholder like "[resume content hidden]" in error output.

After all fixes, do a final grep across the project for common secret patterns:
- Any string matching sk-, Bearer, api_key=, token= (case insensitive)
- Any absolute path containing a username
Report findings but do not print any actual secret values found.
```
