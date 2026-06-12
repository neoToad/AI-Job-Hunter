"""Follow-up email drafter chain.

Generates a short, polite follow-up email for a job application.
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.llm import get_llm


_SYSTEM_TEMPLATE = (
    "You are a polite, concise email assistant. "
    "Draft a brief follow-up email under 100 words. "
    "Do not be pushy, apologetic, or grovel. "
    "Reference the specific role and ask politely about the hiring timeline."
)

_USER_TEMPLATE = """
Company: {company}
Role: {role}
Date Applied: {date_applied}

Draft the follow-up email now.
"""


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
            ("system", _SYSTEM_TEMPLATE),
            ("human", _USER_TEMPLATE),
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
