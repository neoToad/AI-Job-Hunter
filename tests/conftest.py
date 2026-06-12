"""Shared pytest fixtures for the job_search_tool test suite."""

from __future__ import annotations

import pytest

from chains.analyzer import JobAnalysis


@pytest.fixture
def sample_resume_text() -> str:
    return "John Doe\nPython Developer\n5 years experience..."


@pytest.fixture
def sample_job_description() -> str:
    return "We are hiring a Python Developer.\nRequirements:\n- 3+ years Python\n- Django"


@pytest.fixture
def sample_job_analysis() -> JobAnalysis:
    return JobAnalysis(
        company="Acme",
        role="Python Developer",
        must_have=["3+ years Python", "Django"],
        nice_to_have=["AWS"],
        red_flags=[],
        match_score=85,
        matching_skills=["Python", "Django"],
        missing_skills=["AWS"],
        recommendation="apply",
        summary="Strong fit for a Python Developer role.",
    )


@pytest.fixture
def tmp_tracker(tmp_path):
    """Return a path to a fresh tracker pre-seeded with one application row."""
    from utils.tracker import add_application

    path = tmp_path / "tracker.xlsx"
    add_application(path, "Acme", "Engineer", "LinkedIn", 80, "")
    return path


@pytest.fixture
def mock_llm(monkeypatch):
    """Replace ``chains.llm.get_llm`` with a ``FakeListChatModel`` that returns preset strings.

    Patches both the module-level function and the direct imports inside each chain
    module so the mock is respected regardless of how ``get_llm`` was imported.
    """
    from langchain_community.chat_models import FakeListChatModel

    fake = FakeListChatModel(responses=["mock response"])
    monkeypatch.setattr("chains.llm.get_llm", lambda **kwargs: fake)
    monkeypatch.setattr("chains.analyzer.get_llm", lambda **kwargs: fake)
    monkeypatch.setattr("chains.tailorer.get_llm", lambda **kwargs: fake)
    monkeypatch.setattr("chains.cover_letter.get_llm", lambda **kwargs: fake)
    monkeypatch.setattr("chains.followup.get_llm", lambda **kwargs: fake)
    return fake
