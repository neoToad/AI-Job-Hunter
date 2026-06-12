"""Tests for `chains/tailorer`."""

from __future__ import annotations

from langchain_community.chat_models import FakeListChatModel

from chains.tailorer import tailor_resume


VALID_JSON = (
    '{"contact": {"name": "Jane Doe", "email": "jane@example.com"}, '
    '"summary": "Experienced Python dev.", '
    '"experience": [{"title": "Dev", "company": "Acme", "dates": "2020-2022", "bullets": ["Built APIs"]}], '
    '"education": [{"degree": "BS", "school": "State", "dates": "2016-2020"}], '
    '"skills": ["Python", "Django"]}'
)


def test_tailor_resume_returns_dict(monkeypatch, sample_resume_text, sample_job_description, sample_job_analysis) -> None:
    """Return a structured dict when the LLM outputs valid JSON."""
    fake = FakeListChatModel(responses=[VALID_JSON])
    monkeypatch.setattr("chains.tailorer.get_llm", lambda **kwargs: fake)

    result = tailor_resume(sample_resume_text, sample_job_description, sample_job_analysis)
    assert isinstance(result, dict)
    assert result["contact"]["name"] == "Jane Doe"
    assert result["summary"] == "Experienced Python dev."
    assert len(result["experience"]) == 1
    assert result["experience"][0]["title"] == "Dev"
    assert len(result["education"]) == 1
    assert result["skills"] == ["Python", "Django"]


def test_tailor_resume_malformed_json(monkeypatch, sample_resume_text, sample_job_description, sample_job_analysis) -> None:
    """Raise ValueError when the LLM response is not valid JSON."""
    fake = FakeListChatModel(responses=["not valid json"])
    monkeypatch.setattr("chains.tailorer.get_llm", lambda **kwargs: fake)

    import pytest
    with pytest.raises(ValueError, match="unexpected format"):
        tailor_resume(sample_resume_text, sample_job_description, sample_job_analysis)
