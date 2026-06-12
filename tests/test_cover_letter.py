"""Tests for `chains/cover_letter`."""

from __future__ import annotations

from chains.cover_letter import generate_cover_letter


def test_generate_cover_letter_returns_string(mock_llm, sample_resume_text, sample_job_description, sample_job_analysis) -> None:
    """Return the LLM output string when prompt variables are correctly populated."""
    result = generate_cover_letter(sample_resume_text, sample_job_description, sample_job_analysis)
    assert isinstance(result, str)
    assert result == "mock response"
