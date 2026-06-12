"""Follow-up email drafter chain.

Generates a short, polite follow-up email for a job application.

.. note::
    The `.invoke()` call inside `draft_followup` is **not** wrapped in a try/except.
    Callers (CLI, Streamlit UI, tests) are responsible for handling
    `ConnectionError` and other exceptions from the LLM client.
"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from chains.llm import get_llm
from chains.utils import load_prompt


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
            ("system", load_prompt("followup_system.txt")),
            ("human", load_prompt("followup_human.txt")),
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
