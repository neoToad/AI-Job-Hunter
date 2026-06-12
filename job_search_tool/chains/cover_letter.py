"""Cover letter generator chain.

Produces a concise, evidence-based cover letter that maps specific resume
achievements to the job's must-have requirements.
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.analyzer import JobAnalysis
from chains.llm import get_llm


_SYSTEM_TEMPLATE = (
    "You are a direct, no-nonsense cover letter writer. "
    "Write a concise 3–4 paragraph cover letter under 400 words. "
    "Map specific evidence from the resume to specific requirements in the job posting. "
    "Avoid generic filler such as 'I am excited to apply', 'I am a team player', or 'I have always been passionate about'. "
    "Open with a concrete hook, not a cliché."
)

_USER_TEMPLATE = """
RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

COMPANY: {company}
ROLE: {role}

MUST-HAVE REQUIREMENTS:
{must_have}

MATCHING SKILLS FROM THE CANDIDATE:
{matching_skills}

Write the cover letter now. Keep it under 400 words and 3–4 paragraphs.
"""


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
            ("system", _SYSTEM_TEMPLATE),
            ("human", _USER_TEMPLATE),
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
