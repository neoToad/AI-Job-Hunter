"""Job description analyzer chain.

Compares a job description against a resume and returns a structured
`JobAnalysis` with requirements, match score, and recommendation.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from chains.llm import get_llm


class JobAnalysis(BaseModel):
    """Structured output of the job-vs-resume analysis."""

    company: str = Field(description="Name of the hiring company.")
    role: str = Field(description="Job title / role.")
    must_have: list[str] = Field(description="Required skills or qualifications.")
    nice_to_have: list[str] = Field(description="Preferred but not required skills.")
    red_flags: list[str] = Field(description="Potential concerns (e.g., unrealistic requirements, mismatched culture signals).")
    match_score: int = Field(description="Overall fit score from 0 to 100.", ge=0, le=100)
    matching_skills: list[str] = Field(description="Skills the candidate demonstrably has that match the posting.")
    missing_skills: list[str] = Field(description="Skills the candidate lacks that the posting requires.")
    recommendation: Literal["apply", "skip", "stretch"] = Field(
        description="Recruiter recommendation: apply = strong fit, skip = poor fit, stretch = reach role."
    )
    summary: str = Field(description="Brief plain-English summary of the fit.")


_SIGNALS = [
    "responsibilities",
    "requirements",
    "qualifications",
    "experience",
    "skills",
    "role",
    "position",
    "job",
]


def validate_job_description(jd: str) -> tuple[bool, str]:
    """Quick sanity check for a job description string.

    Returns:
        (True, "") if the text looks like a real job posting.
        (False, "reason") if it fails basic heuristics.
    """
    stripped = jd.strip()
    if len(stripped) < 100:
        return False, "Job description is too short (minimum 100 characters)."

    if "\n" not in stripped and stripped.startswith(("http://", "https://")):
        return False, "Input looks like a URL, not a full job description."

    if "\n" not in stripped:
        return False, "Job description is only a single line."

    lowered = stripped.lower()
    if not any(signal in lowered for signal in _SIGNALS):
        return (
            False,
            "Job description is missing typical posting keywords "
            "(e.g., responsibilities, requirements, experience).",
        )

    return True, ""


_SYSTEM_TEMPLATE = (
    "You are an honest, experienced technical recruiter. "
    "Analyze the provided job description against the candidate's resume. "
    "Respond ONLY with valid JSON that exactly matches the requested schema. "
    "Be objective: never invent skills or experience the candidate does not have. "
    "If a requirement is not clearly evidenced in the resume, treat it as missing."
)

_USER_TEMPLATE = """
RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Return your analysis as JSON matching this schema:
{format_instructions}
"""


def analyze_job(resume: str, job_description: str) -> JobAnalysis:
    """Analyze a job description against a resume.

    Args:
        resume: Full text of the candidate's resume.
        job_description: Full text of the job posting.

    Returns:
        A parsed `JobAnalysis` instance.
    """
    parser = JsonOutputParser(pydantic_object=JobAnalysis)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
            ("human", _USER_TEMPLATE),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = get_llm(temperature=0.1)
    chain = prompt | llm | parser

    raw = chain.invoke({"resume": resume, "job_description": job_description})
    # The parser returns a dict; validate it through the Pydantic model.
    return JobAnalysis.model_validate(raw)
