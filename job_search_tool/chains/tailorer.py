"""Resume tailorer chain.

Rewrites a resume to better align with a specific job description,
emphasizing matching skills and incorporating relevant keywords without
inventing experience.
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.analyzer import JobAnalysis
from chains.llm import get_llm


_SYSTEM_TEMPLATE = (
    "You are an expert resume writer who tailors resumes for specific job postings. "
    "Rewrite the candidate's resume bullet points using keywords and phrasing from the job description. "
    "Preserve all existing resume sections (summary, experience, education, skills, etc.). "
    "Use strong action verbs and quantifiable outcomes where possible. "
    "Under no circumstances should you invent experience, skills, or credentials the candidate does not have."
)

_USER_TEMPLATE = """
ORIGINAL RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

MUST-HAVE REQUIREMENTS:
{must_have}

MATCHING SKILLS FROM THE CANDIDATE:
{matching_skills}

Rewrite the resume above so it speaks directly to this job posting while remaining 100% truthful.
"""


def tailor_resume(resume: str, job_description: str, analysis: JobAnalysis) -> str:
    """Return a tailored version of *resume* optimized for *job_description*.

    Args:
        resume: Full text of the original resume.
        job_description: Full text of the job posting.
        analysis: The `JobAnalysis` produced by the analyzer chain (used for
            must-have requirements and matching skills).

    Returns:
        The tailored resume as a plain string.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
            ("human", _USER_TEMPLATE),
        ]
    )

    llm = get_llm(temperature=0.2)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "resume": resume,
            "job_description": job_description,
            "must_have": "\n".join(f"- {item}" for item in analysis.must_have),
            "matching_skills": "\n".join(f"- {item}" for item in analysis.matching_skills),
        }
    )
