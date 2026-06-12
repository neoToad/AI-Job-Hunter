"""Cover letter generator chain.

Produces a concise, evidence-based cover letter that maps specific resume
achievements to the job's must-have requirements.
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.analyzer import JobAnalysis
from chains.llm import get_llm
from chains.utils import load_prompt


def generate_cover_letter(resume: str, job_description: str, analysis: JobAnalysis) -> str:
    """Generate a tailored cover letter.

    Args:
        resume: Full text of the candidate's resume.
        job_description: Full text of the job posting.
        analysis: The `JobAnalysis` produced by the analyzer chain.

    Returns:
        The generated cover letter as a plain string.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("cover_letter_system.txt")),
            ("human", load_prompt("cover_letter_human.txt")),
        ]
    )

    llm = get_llm(temperature=0.5)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "resume": resume,
            "job_description": job_description,
            "company": analysis.company,
            "role": analysis.role,
            "must_have": "\n".join(f"- {item}" for item in analysis.must_have),
            "matching_skills": "\n".join(f"- {item}" for item in analysis.matching_skills),
        }
    )
