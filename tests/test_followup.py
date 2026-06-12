"""Tests for `chains/followup`."""

from __future__ import annotations

from chains.followup import draft_followup


def test_draft_followup_returns_string(mock_llm) -> None:
    """Return the LLM output string when prompt variables are correctly populated."""
    result = draft_followup("Acme", "Engineer", "2024-01-15")
    assert isinstance(result, str)
    assert result == "mock response"
