# Job Search CLI Tool — Prompts 25–27 (Audit & Plan)

## How to Use
Run these after ALL previous prompts (1–24) are complete.
Each prompt scans the codebase and produces a markdown implementation plan.
Do NOT make any code changes during these prompts — output plans only.
Once all three plans are reviewed and approved, run them as separate follow-up prompts.

---

## Prompt 25 — Refactor Audit

```
Scan every file in the job_search_tool project and produce a refactor plan.
Do NOT make any changes. Output only a markdown file saved to:
docs/refactor_plan.md

The plan should identify and document:

1. DUPLICATED LOGIC
   - Any code that appears in more than one file and could be extracted
     into a shared helper (e.g. slug generation, file saving, progress spinners)
   - Note exactly which files contain the duplication and what the shared
     function should be called and where it should live

2. LONG FUNCTIONS
   - Any function over 40 lines that should be broken into smaller pieces
   - For each, suggest what the sub-functions should be named and what they do

3. INCONSISTENT PATTERNS
   - Places where similar things are done differently
     (e.g. one chain uses StrOutputParser, another does .content directly)
   - Places where some functions use Path and others use raw strings
   - Mixed use of f-strings vs .format()

4. DEAD CODE
   - Any imports, variables, or functions that are defined but never used

5. CHAIN STRUCTURE
   - Review all files in chains/ and assess whether any chains are doing
     too much (should be split) or too little (could be merged)
   - Assess whether a LangGraph workflow would be more appropriate than
     the current sequential chain calls in main.py and app.py

6. STREAMLIT & CLI OVERLAP
   - Identify any logic that is duplicated between main.py and app.py
     that should be extracted into a shared pipeline function

For each finding, include:
- File name and line numbers
- What the problem is
- What the fix should be
- Estimated complexity: Low / Medium / High

At the end, produce a prioritized list of all refactors ordered by impact vs effort.
```

---

## Prompt 26 — Best Practices Audit

```
Scan every file in the job_search_tool project and produce a best practices plan.
Do NOT make any changes. Output only a markdown file saved to:
docs/best_practices_plan.md

The plan should check and document findings in these categories:

1. TYPE HINTS
   - Every function signature should have full type hints on all parameters and return type
   - List every function that is missing any type hint

2. DOCSTRINGS
   - Every public function and class should have a docstring
   - List every function missing one
   - Flag any docstring that is misleading or out of date with the actual implementation

3. ERROR HANDLING
   - Any LLM call not wrapped in try/except
   - Any file read/write not wrapped in try/except
   - Any place where a raw Python exception could surface to the user
   - Any place where an error is silently swallowed (bare except or pass)

4. ENVIRONMENT & CONFIG
   - Any hardcoded values that should be in .env / config.py
   - Any config values read directly via os.getenv() outside of config.py
   - Verify .env.example matches every value consumed in config.py

5. SECURITY
   - Any place where user input is passed unsanitized to a file path
     (path traversal risk — e.g. company name used directly in filename)
   - Any place where a URL is fetched without a timeout
   - Any place where exceptions might expose sensitive info (resume content in tracebacks)

6. LANGCHAIN BEST PRACTICES
   - Check all chains use LCEL pipe syntax (prompt | llm | parser)
   - Check temperature values are appropriate for each task
     (low for structured output, higher for creative writing)
   - Check all prompts explicitly instruct the model on output format
   - Flag any prompt that relies on the model "just knowing" what to do

7. STREAMLIT BEST PRACTICES
   - Check that st.session_state is used for any data that should persist
     across reruns (e.g. analysis results, so they don't disappear on button click)
   - Check that long-running chain calls are wrapped in st.spinner()
   - Check that all user-facing error messages use st.error() not st.write()

For each finding, include:
- File name and line numbers
- What the issue is
- What the fix should be
- Severity: Critical / Major / Minor

At the end, produce a prioritized list ordered by severity.
```

---

## Prompt 27 — Testing Audit

```
Scan every file in the job_search_tool project and produce a testing plan.
Do NOT make any changes. Output only a markdown file saved to:
docs/testing_plan.md

The plan should cover:

1. WHAT TO TEST
   For each file, identify the functions that most need tests and why:
   - utils/resume_parser.py
   - utils/tracker.py
   - chains/analyzer.py
   - chains/tailorer.py
   - chains/cover_letter.py
   - chains/followup.py
   - config.py
   - main.py (CLI commands)
   - app.py (Streamlit)

2. TEST CASES TO WRITE
   For each function identified, list the specific test cases needed:
   - Happy path (normal valid input)
   - Edge cases (empty input, missing files, very long input)
   - Failure cases (bad PDF, unreachable Ollama, malformed JSON from LLM)
   
   Format each test case as:
   - Function: `parse_resume()`
   - Test: "returns ValueError when PDF has no extractable text"
   - Type: Unit
   - Mock needed: None / pdfplumber / LLM / filesystem

3. MOCKING STRATEGY
   - Identify everything that needs to be mocked for unit tests
     (LLM calls, file system, Ollama API, Excel files)
   - Recommend whether to use unittest.mock, pytest-mock, or LangChain's
     built-in fake LLMs (FakeListChatModel) for chain testing
   - Provide a sample mock setup for the LLM so test cases don't make
     real Ollama calls

4. TEST STRUCTURE
   Recommend a directory layout:
   tests/
   ├── conftest.py          (shared fixtures)
   ├── test_resume_parser.py
   ├── test_tracker.py
   ├── test_analyzer.py
   ├── test_tailorer.py
   ├── test_cover_letter.py
   ├── test_followup.py
   └── test_cli.py

   For conftest.py, specify exactly what fixtures should be defined:
   - A sample resume text string
   - A sample job description string
   - A sample JobAnalysis object
   - A tmp_path-based tracker fixture
   - A mock LLM fixture using FakeListChatModel

5. COVERAGE GOALS
   - Identify the minimum viable test suite (highest value, lowest effort tests)
   - Identify which functions are risky to leave untested and why
   - Recommend a target coverage percentage for each module

6. CI RECOMMENDATION
   - Suggest a simple GitHub Actions workflow file (.github/workflows/test.yml)
     that installs dependencies and runs pytest on every push
   - Note which tests should be skipped in CI
     (anything requiring a real Ollama connection)

At the end, produce a prioritized list of tests to write ordered by risk —
highest risk untested code first.
```
