"""Streamlit UI for the job search tool.

Provides two modes:
- Analyze Job: run the analyzer chain and display structured results.
- Full Application: run the full pipeline (analyze, tailor, cover letter, tracker update).

All business logic is imported from chains/ and utils/ — no duplication.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import config
from chains.analyzer import analyze_job
from chains.cover_letter import generate_cover_letter
from chains.tailorer import tailor_resume
from utils.resume_parser import parse_resume
from utils.tracker import add_application, application_exists


st.set_page_config(page_title="Job Search Assistant", layout="wide")

# --- Sidebar -----------------------------------------------------------------

st.sidebar.title("Job Search Assistant")
mode = st.sidebar.radio("Mode", ["Analyze Job", "Full Application"])

job_source = ""
if mode == "Full Application":
    job_source = st.sidebar.text_input("Job Source (e.g., LinkedIn, Adzuna)")

# --- Main panel --------------------------------------------------------------

st.header(mode)
job_description = st.text_area("Paste job description here", height=300)

dry_run = False
if mode == "Full Application":
    dry_run = st.checkbox("Dry run (analyze only, don't save)")

button_label = "Analyze" if mode == "Analyze Job" else "Apply"
run_clicked = st.button(button_label, type="primary")


# --- Cached resume parsing (one per session) -----------------------------------

@st.cache_resource(show_spinner="Parsing resume...")
def _cached_resume_text() -> str:
    """Parse the resume once per Streamlit session."""
    if not config.RESUME_PATH.exists():
        raise FileNotFoundError(f"Resume not found at {config.RESUME_PATH}")
    return parse_resume(config.RESUME_PATH)


# --- Analyze Job mode --------------------------------------------------------

if mode == "Analyze Job" and run_clicked:
    if not job_description.strip():
        st.warning("Please paste a job description first.")
        st.stop()

    try:
        resume_text = _cached_resume_text()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    except ValueError:
        st.error(
            "Could not parse resume. Try re-saving it as a text-based PDF."
        )
        st.stop()

    with st.spinner("Analyzing job..."):
        try:
            result = analyze_job(resume_text, job_description)
        except ConnectionError:
            st.error(
                "Cannot reach Ollama. Is it running? Try: ollama serve"
            )
            st.stop()
        except Exception as exc:
            st.error(f"Error during analysis: {exc}")
            st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Match Score", f"{result.match_score}/100")
    with col2:
        rec = result.recommendation
        if rec == "apply":
            st.success("Recommendation: APPLY")
        elif rec == "stretch":
            st.warning("Recommendation: STRETCH")
        else:
            st.error("Recommendation: SKIP")

    st.markdown(f"**Summary:** {result.summary}")

    if result.must_have:
        with st.expander("Must-Have Requirements"):
            for req in result.must_have:
                st.write(f"- {req}")

    if result.matching_skills:
        with st.expander("Matching Skills"):
            for skill in result.matching_skills:
                st.write(f"- {skill}")

    if result.missing_skills:
        with st.expander("Missing Skills"):
            for skill in result.missing_skills:
                st.write(f"- {skill}")

    if result.red_flags:
        with st.expander("Red Flags"):
            for flag in result.red_flags:
                st.write(f"- {flag}")

    if result.nice_to_have:
        with st.expander("Nice-to-Have"):
            for req in result.nice_to_have:
                st.write(f"- {req}")

# --- Full Application mode ---------------------------------------------------

if mode == "Full Application" and run_clicked:
    if not job_description.strip():
        st.warning("Please paste a job description first.")
        st.stop()

    try:
        resume_text = _cached_resume_text()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    except ValueError:
        st.error(
            "Could not parse resume. Try re-saving it as a text-based PDF."
        )
        st.stop()

    progress_bar = st.progress(0, text="Analyzing job...")

    try:
        analysis = analyze_job(resume_text, job_description)
    except ConnectionError:
        st.error("Cannot reach Ollama. Is it running? Try: ollama serve")
        st.stop()
    except Exception as exc:
        st.error(f"Error during analysis: {exc}")
        st.stop()

    progress_bar.progress(25, text="Analysis complete")

    # Display analysis results
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Match Score", f"{analysis.match_score}/100")
    with col2:
        rec = analysis.recommendation
        if rec == "apply":
            st.success("Recommendation: APPLY")
        elif rec == "stretch":
            st.warning("Recommendation: STRETCH")
        else:
            st.error("Recommendation: SKIP")

    st.markdown(f"**Summary:** {analysis.summary}")

    if dry_run:
        st.info("Dry run — nothing saved")
        st.stop()

    # Duplicate check
    duplicate = application_exists(config.TRACKER_PATH, analysis.company, analysis.role)
    if duplicate:
        st.warning(
            "An application for this company and role already exists in the tracker. "
            "Check the box below to proceed anyway."
        )
        confirm_duplicate = st.checkbox("I want to proceed despite the duplicate")
        if not confirm_duplicate:
            st.stop()

    # Tailor resume
    progress_bar.progress(50, text="Tailoring resume...")
    try:
        tailored_resume = tailor_resume(resume_text, job_description, analysis)
    except ConnectionError:
        st.error("Cannot reach Ollama. Is it running? Try: ollama serve")
        st.stop()
    except Exception as exc:
        st.error(f"Error tailoring resume: {exc}")
        st.stop()

    # Generate cover letter
    progress_bar.progress(75, text="Generating cover letter...")
    try:
        cover_letter = generate_cover_letter(resume_text, job_description, analysis)
    except ConnectionError:
        st.error("Cannot reach Ollama. Is it running? Try: ollama serve")
        st.stop()
    except Exception as exc:
        st.error(f"Error generating cover letter: {exc}")
        st.stop()

    # Save outputs
    from utils.helpers import make_slug

    slug = make_slug(analysis.company, analysis.role)
    resume_out = config.TAILORED_RESUMES_DIR / f"resume_{slug}"
    cl_out = config.COVER_LETTERS_DIR / f"cover_letter_{slug}"

    try:
        resume_out.write_text(tailored_resume, encoding="utf-8")
        cl_out.write_text(cover_letter, encoding="utf-8")
    except OSError as exc:
        st.error(f"Error saving files: {exc}")
        st.stop()

    # Update tracker
    try:
        add_application(
            path=config.TRACKER_PATH,
            company=analysis.company,
            role=analysis.role,
            source=job_source,
            match_score=analysis.match_score,
            notes="",
            cover_letter_path=cl_out,
        )
    except Exception as exc:
        st.error(f"Error updating tracker: {exc}")
        st.stop()

    progress_bar.progress(100, text="Done!")
    st.success("Application logged successfully!")

    st.subheader("Cover Letter")
    st.text_area("Editable cover letter", value=cover_letter, height=250)

    st.subheader("Tailored Resume")
    st.text_area("Editable tailored resume", value=tailored_resume, height=250)
