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
from chains.utils import load_prompt


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
            ("system", load_prompt("tailorer_system.txt")),
            ("human", load_prompt("tailorer_human.txt")),
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
