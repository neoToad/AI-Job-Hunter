"""Shared application pipeline.

Provides a single entry point that both the CLI and the Streamlit UI can call
to run the full apply flow (analyze → tailor → cover letter → save → tracker).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from chains.analyzer import JobAnalysis, analyze_job
from chains.cover_letter import generate_cover_letter
from chains.tailorer import tailor_resume
from utils.helpers import make_slug
from utils.renderers import render_cover_letter_docx, render_resume_pdf
from utils.tracker import add_application

import config


class PipelineStep(Enum):
    """Discrete steps emitted by ``run_apply_pipeline`` via the *on_step* callback."""

    ANALYZING = auto()
    TAILORING = auto()
    SAVING = auto()
    DONE = auto()


@dataclass
class PipelineResult:
    """Output of the full application pipeline."""

    analysis: JobAnalysis
    tailored_resume: dict | str
    cover_letter: str
    saved_paths: dict[str, Path]


def run_apply_pipeline(
    resume: str,
    job_description: str,
    source: str,
    skip_tailor: bool,
    dry_run: bool,
    *,
    analysis: JobAnalysis | None = None,
    notes: str = "",
    on_step: Callable[[PipelineStep], None] | None = None,
) -> PipelineResult:
    """Run the full application pipeline.

    The pipeline consists of:
    1. Job analysis (skipped if *analysis* is provided).
    2. Resume tailoring and cover-letter generation (skipped if *dry_run*).
    3. Writing files to disk (skipped if *dry_run*).
    4. Updating the application tracker (skipped if *dry_run*).

    Args:
        resume: Full text of the candidate's resume.
        job_description: Full text of the job posting.
        source: Where the posting was found (e.g., LinkedIn, Indeed).
        skip_tailor: If ``True``, skip resume tailoring.
        dry_run: If ``True``, run analysis only and return without saving.
        analysis: Optional pre-computed ``JobAnalysis``. When provided, step 1
            is skipped and the existing result is reused.
        notes: Free-text notes for the tracker entry.
        on_step: Optional callback invoked after each major pipeline step.
            Useful for updating UI progress bars.

    Returns:
        A ``PipelineResult`` containing the analysis, tailored resume, cover
        letter, and a dictionary of saved file paths.
    """
    _emit = on_step or (lambda _s: None)

    # --- Step 1: Analysis ----------------------------------------------------
    _emit(PipelineStep.ANALYZING)
    if analysis is None:
        analysis = analyze_job(resume, job_description)

    if dry_run:
        return PipelineResult(
            analysis=analysis,
            tailored_resume=resume,
            cover_letter="",
            saved_paths={},
        )

    # --- Step 2: Tailoring + Cover Letter ------------------------------------
    _emit(PipelineStep.TAILORING)
    if skip_tailor:
        tailored_resume = resume
        cover_letter = generate_cover_letter(resume, job_description, analysis)
    else:
        async def _tailor_and_cover():
            return await asyncio.gather(
                asyncio.to_thread(tailor_resume, resume, job_description, analysis),
                asyncio.to_thread(
                    generate_cover_letter, resume, job_description, analysis
                ),
            )

        tailored_resume, cover_letter = asyncio.run(_tailor_and_cover())

    # --- Step 3: Save outputs ------------------------------------------------
    _emit(PipelineStep.SAVING)
    slug = make_slug(analysis.company, analysis.role)
    resume_out = config.TAILORED_RESUMES_DIR / f"resume_{slug}.pdf"
    cl_out = config.COVER_LETTERS_DIR / f"cover_letter_{slug}.docx"

    if skip_tailor:
        # Original resume text is a string; fall back to plain text.
        resume_out = resume_out.with_suffix(".txt")
        resume_out.write_text(tailored_resume, encoding="utf-8")
    else:
        render_resume_pdf(tailored_resume, resume_out)
    render_cover_letter_docx(cover_letter, cl_out)

    # --- Step 4: Update tracker ----------------------------------------------
    add_application(
        path=config.TRACKER_PATH,
        company=analysis.company,
        role=analysis.role,
        source=source,
        match_score=analysis.match_score,
        notes=notes,
        cover_letter_path=cl_out,
    )

    _emit(PipelineStep.DONE)

    return PipelineResult(
        analysis=analysis,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
        saved_paths={"resume": resume_out, "cover_letter": cl_out},
    )
