"""Follow-up email drafter chain.

Generates a short, polite follow-up email for a job application.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.llm import get_llm


def _load_prompt(name: str) -> str:
    """Load a prompt template from the ``prompts/`` directory."""
    return (Path(__file__).parent.parent / "prompts" / name).read_text()


def draft_followup(company: str, role: str, date_applied: str) -> str:
    """Draft a polite follow-up email for a job application.

    Args:
        company: Name of the hiring company.
        role: Job title / role applied for.
        date_applied: ISO-formatted or human-readable date the application was sent.

    Returns:
        The drafted follow-up email as a plain string.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _load_prompt("followup_system.txt")),
            ("human", _load_prompt("followup_human.txt")),
        ]
    )

    llm = get_llm(temperature=0.4)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke(
        {
            "company": company,
            "role": role,
            "date_applied": date_applied,
        }
    )
