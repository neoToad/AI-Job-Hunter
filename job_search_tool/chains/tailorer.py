"""Resume tailorer chain.

Rewrites a resume to better align with a specific job description,
emphasizing matching skills and incorporating relevant keywords without
inventing experience.

.. note::
    The `.invoke()` call inside `tailor_resume` is **not** wrapped in a try/except.
    Callers (CLI, Streamlit UI, tests) are responsible for handling
    `ConnectionError` and other exceptions from the LLM client.
"""

from __future__ import annotations

from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from chains.analyzer import JobAnalysis
from chains.llm import get_llm
from chains.utils import load_prompt


class ExperienceEntry(BaseModel):
    """A single work-experience entry."""

    title: str = Field(description="Job title held at the company.")
    company: str = Field(description="Employer name.")
    dates: str = Field(description="Employment dates (e.g., 'Jan 2020 – Dec 2022').")
    bullets: list[str] = Field(description="Achievement bullets rewritten for the target role.")


class TailoredResume(BaseModel):
    """Structured JSON representation of a tailored resume."""

    contact: dict[str, str] = Field(
        description="Contact info: name, email, phone, location, linkedin."
    )
    summary: str = Field(description="Professional summary paragraph.")
    experience: list[ExperienceEntry] = Field(description="Work history entries.")
    education: list[dict[str, str]] = Field(
        description="Education entries with keys: degree, school, dates."
    )
    skills: list[str] = Field(description="Relevant skills for the target role.")


def tailor_resume(resume: str, job_description: str, analysis: JobAnalysis) -> dict[str, Any]:
    """Return a tailored version of *resume* optimized for *job_description*.

    Args:
        resume: Full text of the original resume.
        job_description: Full text of the job posting.
        analysis: The `JobAnalysis` produced by the analyzer chain (used for
            must-have requirements and matching skills).

    Returns:
        A structured dictionary representing the tailored resume with keys:
        ``contact``, ``summary``, ``experience``, ``education``, ``skills``.

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON matching
            the expected schema.
    """
    parser = JsonOutputParser(pydantic_object=TailoredResume)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("tailorer_system.txt")),
            ("human", load_prompt("tailorer_human.txt")),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = get_llm(temperature=0.2)
    chain = prompt | llm | parser

    try:
        raw = chain.invoke(
            {
                "resume": resume,
                "job_description": job_description,
                "must_have": "\n".join(f"- {item}" for item in analysis.must_have),
                "matching_skills": "\n".join(f"- {item}" for item in analysis.matching_skills),
            }
        )
    except OutputParserException as exc:
        raise ValueError(
            "AI returned unexpected format. Try running again."
        ) from exc

    # Validate through the Pydantic model and return as a plain dict.
    validated = TailoredResume.model_validate(raw)
    return validated.model_dump()
