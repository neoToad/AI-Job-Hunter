"""Configuration loader for the job search tool.

Loads all settings from a .env file (if present) and exposes them as
module-level constants. Also ensures all required output directories
exist when this module is imported.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.console import Console

# Load .env from the project root (job_search_tool/).
# Safe to call even if the file doesn't exist — values fall back to defaults.
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")


# --- LLM configuration -------------------------------------------------------

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_API_KEY: str | None = os.getenv("OLLAMA_API_KEY") or None


# --- File paths --------------------------------------------------------------
# All paths are resolved relative to the project root so the tool works
# regardless of the current working directory it is invoked from.

def _resolve(path_str: str) -> Path:
    """Resolve a path string: absolute paths are kept, relative ones
    are anchored at the project root."""
    p = Path(path_str)
    return p if p.is_absolute() else (_PROJECT_ROOT / p)


RESUME_PATH: Path = _resolve(os.getenv("RESUME_PATH", "resume/resume.pdf"))
TRACKER_PATH: Path = _resolve(os.getenv("TRACKER_PATH", "data/tracker.xlsx"))
OUTPUT_DIR: Path = _resolve(os.getenv("OUTPUT_DIR", "output"))

# Derived output subdirectories
COVER_LETTERS_DIR: Path = OUTPUT_DIR / "cover_letters"
TAILORED_RESUMES_DIR: Path = OUTPUT_DIR / "tailored_resumes"


# --- Ensure output directories exist ----------------------------------------
# Creating them on import means downstream code (chains, utils) can always
# assume the directories are present and writable.

for _dir in (OUTPUT_DIR, COVER_LETTERS_DIR, TAILORED_RESUMES_DIR, RESUME_PATH.parent, TRACKER_PATH.parent):
    _dir.mkdir(parents=True, exist_ok=True)


# --- Config validation -------------------------------------------------------

def validate_config(console: Console | None = None) -> None:
    """Check for common misconfiguration issues and print warnings.

    Warnings are non-blocking. Call once at startup.
    """
    _console = console or Console()

    if not os.getenv("OLLAMA_MODEL"):
        _console.print(
            "[bold yellow]Warning:[/] No model set, defaulting to llama3.1"
        )

    parsed = urlparse(OLLAMA_BASE_URL)
    if parsed.hostname in ("localhost", "127.0.0.1", "::1"):
        port = parsed.port or 11434
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex((str(parsed.hostname), port)) != 0:
                _console.print(
                    "[bold yellow]Warning:[/] Ollama may not be running locally"
                )

    if not RESUME_PATH.exists():
        _console.print(
            f"[bold yellow]Warning:[/] Resume not found at {RESUME_PATH}"
        )
