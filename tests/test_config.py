"""Tests for `config`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import config


def test_validate_config_no_warnings_when_valid(monkeypatch) -> None:
    """Print no warnings when resume exists, model is set, and Ollama port is open."""
    mock_console = MagicMock()
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=True)))

    with patch("config.os.getenv", return_value="llama3.1"):
        with patch("config.socket.socket") as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_sock_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_sock_cls.return_value.__exit__ = MagicMock(return_value=False)
            config.validate_config(mock_console)

    mock_console.print.assert_not_called()


def test_validate_config_warns_when_resume_missing(monkeypatch) -> None:
    """Print a warning when the resume file does not exist."""
    mock_console = MagicMock()
    monkeypatch.setattr(config, "RESUME_PATH", MagicMock(spec=Path, exists=MagicMock(return_value=False)))

    with patch("config.os.getenv", return_value="llama3.1"):
        with patch("config.socket.socket") as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_sock_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_sock_cls.return_value.__exit__ = MagicMock(return_value=False)
            config.validate_config(mock_console)

    mock_console.print.assert_called_once()
    assert "Resume not found" in mock_console.print.call_args[0][0]
