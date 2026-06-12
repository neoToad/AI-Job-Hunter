"""Tests for `chains/analyzer`."""

from __future__ import annotations

import pytest
from langchain_community.chat_models import FakeListChatModel

from chains.analyzer import JobAnalysis, analyze_job, validate_job_description


# ---------------------------------------------------------------------------
# validate_job_description
# ---------------------------------------------------------------------------


def test_validate_job_description_realistic() -> None:
    jd = (
        "We are hiring a Python Developer.\n"
        "Responsibilities:\n"
        "- Build APIs\n"
        "Requirements:\n"
        "- 3+ years Python\n"
        "- Django experience"
    )
    is_valid, reason = validate_job_description(jd)
    assert is_valid is True
    assert reason == ""


def test_validate_job_description_too_short() -> None:
    is_valid, reason = validate_job_description("short")
    assert is_valid is False
    assert "too short" in reason.lower()


def test_validate_job_description_url_only() -> None:
    is_valid, reason = validate_job_description(
        "https://example.com/job/123 " + "x" * 200
    )
    assert is_valid is False
    assert "URL" in reason


def test_validate_job_description_missing_keywords() -> None:
    jd = (
        "We need someone to do some work.\n"
        "It is an opening.\n"
        "Apply now if you are interested.\n"
        "This is a great opportunity for the right candidate.\n"
        "Please send your cv today.\n" + "x" * 100
    )
    is_valid, reason = validate_job_description(jd)
    assert is_valid is False
    assert "missing" in reason.lower()


# ---------------------------------------------------------------------------
# analyze_job
# ---------------------------------------------------------------------------


def test_analyze_job_valid_json(monkeypatch) -> None:
    valid_json = (
        '{"company": "Acme", "role": "Python Developer", '
        '"must_have": ["3+ years Python"], "nice_to_have": ["AWS"], '
        '"red_flags": [], "match_score": 85, "matching_skills": ["Python"], '
        '"missing_skills": ["AWS"], "recommendation": "apply", '
        '"summary": "Strong fit."}'
    )
    fake = FakeListChatModel(responses=[valid_json])
    monkeypatch.setattr("chains.analyzer.get_llm", lambda **kwargs: fake)

    result = analyze_job("resume text", "job description")
    assert isinstance(result, JobAnalysis)
    assert result.company == "Acme"
    assert result.role == "Python Developer"
    assert result.match_score == 85


def test_analyze_job_malformed_json(monkeypatch) -> None:
    fake = FakeListChatModel(responses=["not valid json"])
    monkeypatch.setattr("chains.analyzer.get_llm", lambda **kwargs: fake)

    with pytest.raises(ValueError, match="unexpected format"):
        analyze_job("resume text", "job description")
