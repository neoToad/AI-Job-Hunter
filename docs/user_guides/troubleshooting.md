# Troubleshooting Guide

Common failure modes and how to fix them.

---

## Ollama Not Reachable

**Symptom:**
```
Error: Cannot reach Ollama.
Hint: Is it running? Try: ollama serve
```

**Causes & Fixes:**

1. **Ollama is not running**
   - Fix: Start it with `ollama serve` (or launch the Ollama desktop app).

2. **Wrong base URL in `.env`**
   - Check that `OLLAMA_BASE_URL` matches where Ollama is listening.
   - Default: `http://localhost:11434`
   - If you changed the port, update `.env` accordingly.

3. **Firewall or VPN blocking the port**
   - Test connectivity manually:
     ```bash
     curl http://localhost:11434/api/tags
     ```
   - If that hangs, the port is blocked. Allow port 11434 in your firewall or switch to Ollama Cloud Pro.

4. **Model not pulled**
   - If Ollama runs but the verify command warns that the model is missing:
     ```bash
     ollama pull llama3.1
     ```

---

## Resume PDF Won't Parse

**Symptom:**
```
Error: Could not parse resume.
Hint: Try re-saving it as a text-based PDF.
```

**Causes & Fixes:**

1. **PDF is image-based (scanned)**
   - `pdfplumber` can only extract text from text-based PDFs.
   - Fix: Open the PDF in a PDF reader, print to PDF, or run OCR first (e.g., Adobe Acrobat, macOS Preview Export as PDF).

2. **Resume is not at the expected path**
   - Default: `job_search_tool/resume/resume.pdf`
   - Fix: Move your PDF there, or update `RESUME_PATH` in `.env`.

3. **Partial parse (some pages empty)**
   - If you see warnings like:
     ```
     Warning: page 2 of resume.pdf returned no text — it may be image-based
     ```
     but the tool still proceeds, the remaining pages had enough text. Consider re-saving the PDF anyway.

---

## LLM Returns Malformed JSON

**Symptom:**
```
Error: AI returned unexpected format. Try running again.
```

**Causes & Fixes:**

1. **Model hallucinated invalid JSON**
   - Fix: Simply re-run `python main.py analyze`. Most of the time it self-corrects.

2. **Temperature too high for structured output**
   - The analyzer uses `temperature=0.1`, which is already low. If your model does not support temperature adjustment well, consider switching to a stronger model (e.g., `llama3.1`, `mistral`, `qwen2.5`).

3. **Prompt file got corrupted**
   - Make sure `prompts/analyzer_system.txt` still contains the full JSON schema example. If you edited it, verify the braces and quotes are balanced.

4. **Job description is extremely short or garbled**
   - The analyzer needs at least ~100 characters of coherent text. Use a longer posting or copy the description manually.

---

## Tracker File Is Locked (PermissionError)

**Symptom:**
```
Error: Error updating tracker: [Errno 13] Permission denied: 'data/tracker.xlsx'
```

**Cause:**
The tracker file is open in Excel, LibreOffice, or another program that holds a write lock.

**Fix:**
Close the spreadsheet in the other program, then retry the command. You can view the tracker with `python main.py tracker --show` without opening it in Excel.

---

## URL Fetch Fails or Returns Empty Content

**Symptom:**
```
Warning: Extracted only 45 characters from the page.
The job description may be hidden behind JavaScript or loaded dynamically.
```

**Causes & Fixes:**

1. **Page requires JavaScript to render the job description**
   - Many modern job boards load content dynamically. The tool fetches raw HTML and strips scripts, so dynamic content is lost.
   - Fix: Manually copy the job description into a text file and use `--file` instead of `--url`.

2. **URL is behind a login wall or geo-blocked**
   - Fix: Copy the text manually and use `--file`.

3. **URL scheme is invalid**
   - Only `http://` and `https://` are accepted. `ftp://` or `file://` will be rejected with a clear error.

4. **Request timed out**
   - The tool uses a 10-second timeout. Slow pages may fail.
   - Fix: Use `--file` or retry.

---

## Streamlit Won't Start

**Symptom:**
```
command not found: streamlit
```
or
```
Port 8501 is already in use.
```

**Causes & Fixes:**

1. **Streamlit not installed**
   - Fix: `pip install streamlit` (it is already in `requirements.txt`, so re-run `pip install -r requirements.txt`).

2. **Port 8501 is occupied**
   - Fix: Use a different port:
     ```bash
     streamlit run app.py --server.port 8502
     ```

3. **Running from the wrong directory**
   - You must run from `job_search_tool/` so that `config.py` resolves paths correctly:
     ```bash
     cd job_search_tool
     streamlit run app.py
     ```

4. **Module not found errors inside the app**
   - This usually means the virtual environment is not activated or dependencies are incomplete.
   - Fix: `pip install -r requirements.txt` from the activated environment.

---

## General Tips

- **Run `python main.py verify` first** whenever something feels off. It checks resume parsing, Ollama reachability, and model availability in one shot.
- **Check `.env`** if paths or URLs seem wrong. The file is loaded on every run.
- **Keep `data/tracker.xlsx` closed** while running commands to avoid permission errors.
