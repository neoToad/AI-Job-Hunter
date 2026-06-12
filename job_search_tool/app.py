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
from utils.resume_parser import get_resume_text
from utils.tracker import application_exists


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
    """Parse the resume once per Streamlit session.

    Raises:
        FileNotFoundError: If the resume PDF does not exist.
        ValueError: If no text could be extracted from the PDF.
    """
    return get_resume_text(config.RESUME_PATH)


# --- Session-state helpers ----------------------------------------------------

def _clear_stale_state(current_jd: str, current_mode: str) -> None:
    """Remove cached results if the job description or mode has changed."""
    last_jd = st.session_state.get("last_job_description", "")
    last_mode = st.session_state.get("last_mode", "")
    if last_jd != current_jd or last_mode != current_mode:
        for key in ("analyze_result", "analysis", "tailored_resume", "cover_letter", "apply_complete"):
            st.session_state.pop(key, None)
        st.session_state.last_job_description = current_jd
        st.session_state.last_mode = current_mode


# --- Analyze Job mode --------------------------------------------------------

if mode == "Analyze Job":
    _clear_stale_state(job_description, mode)

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

    st.session_state.analyze_result = result

if mode == "Analyze Job" and "analyze_result" in st.session_state:
    result = st.session_state.analyze_result

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

    _SECTION_TITLES = {
        "must_have": "Must-Have Requirements",
        "matching_skills": "Matching Skills",
        "missing_skills": "Missing Skills",
        "red_flags": "Red Flags",
        "nice_to_have": "Nice-to-Have",
    }

    for key, items in result.to_display_dict().items():
        if items:
            with st.expander(_SECTION_TITLES[key]):
                for item in items:
                    st.write(f"- {item}")

# --- Full Application mode ---------------------------------------------------

if mode == "Full Application":
    _clear_stale_state(job_description, mode)

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

    from pipelines import PipelineStep, run_apply_pipeline

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

    st.session_state.analysis = analysis

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

    def _on_step(step: PipelineStep) -> None:
        if step == PipelineStep.ANALYZING:
            progress_bar.progress(25, text="Analyzing job...")
        elif step == PipelineStep.TAILORING:
            progress_bar.progress(50, text="Tailoring resume & generating cover letter...")
        elif step == PipelineStep.SAVING:
            progress_bar.progress(75, text="Saving outputs...")
        elif step == PipelineStep.DONE:
            progress_bar.progress(100, text="Done!")

    try:
        result = run_apply_pipeline(
            resume_text,
            job_description,
            source=job_source,
            skip_tailor=False,
            dry_run=False,
            analysis=analysis,
            on_step=_on_step,
        )
    except ConnectionError:
        st.error("Cannot reach Ollama. Is it running? Try: ollama serve")
        st.stop()
    except Exception as exc:
        st.error(f"Error during pipeline: {exc}")
        st.stop()

    st.session_state.tailored_resume = result.tailored_resume
    st.session_state.cover_letter = result.cover_letter
    st.session_state.apply_complete = True
    st.success("Application logged successfully!")

if mode == "Full Application" and "analysis" in st.session_state:
    analysis = st.session_state.analysis

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

    if st.session_state.get("apply_complete"):
        st.subheader("Cover Letter")
        st.text_area(
            "Editable cover letter",
            height=250,
            key="cover_letter",
        )

        st.subheader("Tailored Resume")
        st.text_area(
            "Editable tailored resume",
            height=250,
            key="tailored_resume",
        )
