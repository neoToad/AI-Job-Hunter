"""CLI entry point for the job search tool.

The full Typer app is built in Prompt 9. For now this is a stub that
verifies the scaffold loads correctly (config + paths are wired up).
"""

from __future__ import annotations

import typer
from rich.console import Console

import config

app = typer.Typer(help="Job search automation CLI.")
console = Console()


@app.command()
def verify() -> None:
    """Confirm the scaffold is wired up: print resolved paths and confirm
    output directories exist."""
    console.print("[bold green]job_search_tool scaffold OK[/bold green]")
    console.print(f"  Resume path:        {config.RESUME_PATH}")
    console.print(f"  Tracker path:       {config.TRACKER_PATH}")
    console.print(f"  Output dir:         {config.OUTPUT_DIR}")
    console.print(f"  Cover letters dir:  {config.COVER_LETTERS_DIR}")
    console.print(f"  Tailored resumes:   {config.TAILORED_RESUMES_DIR}")
    console.print(f"  Ollama URL:         {config.OLLAMA_BASE_URL}")
    console.print(f"  Ollama model:       {config.OLLAMA_MODEL}")


if __name__ == "__main__":
    app()