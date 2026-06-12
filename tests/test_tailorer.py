"""Tests for `chains/tailorer`."""

from __future__ import annotations

from chains.tailorer import tailor_resume


def test_tailor_resume_returns_string(mock_llm, sample_resume_text, sample_job_description, sample_job_analysis) -> None:
    """Return the LLM output string when prompt variables are correctly populated."""
    result = tailor_resume(sample_resume_text, sample_job_description, sample_job_analysis)
    assert isinstance(result, str)
    assert result == "mock response"
