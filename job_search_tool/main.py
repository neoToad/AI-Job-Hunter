"""CLI entry point for the job search tool.

Provides Typer commands: verify, analyze, apply, followup, tracker.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, TypeVar

import asyncio
import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

import config
from chains.analyzer import JobAnalysis, analyze_job, validate_job_description
from utils.helpers import fetch_url_text, handle_error, make_slug
from utils.resume_parser import get_resume_text, preview_resume
from utils.tracker import (
    add_application,
    application_exists,
    delete_application,
    edit_application,
    get_followups_due,
    show_tracker,
    update_status,
)

app = typer.Typer(help="Job search automation CLI.")
console = Console()


def _parse_resume_for_cli() -> str:
    """Parse the resume with a CLI spinner and uniform error handling.

    Returns:
        The full text of the resume.

    Raises:
        typer.Exit: If the resume is missing or cannot be parsed.
    """
    with console.status("[bold green]Parsing resume..."):
        try:
            return get_resume_text(config.RESUME_PATH)
        except FileNotFoundError:
            handle_error(
                f"Resume not found at {config.RESUME_PATH}",
                hint="Place your PDF at resume/resume.pdf",
            )
        except ValueError:
            handle_error(
                "Could not parse resume.",
                hint="Try re-saving it as a text-based PDF.",
            )


T = TypeVar("T")


def _run_chain_with_spinner(
    description: str,
    fn: Callable[[], T],
    step_name: str = "",
) -> T:
    """Run *fn* inside a Rich spinner with generic exception handling.

    Args:
        description: Text shown next to the spinner.
        fn: Callable that performs the LLM work.
        step_name: Human-readable name used in the generic error message.
            Falls back to *description* if omitted.

    Returns:
        Whatever *fn* returns.

    Raises:
        typer.Exit: On ConnectionError or any unexpected exception.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description=description, total=None)
        try:
            return fn()
        except ConnectionError:
            handle_error(
                "Cannot reach Ollama.",
                hint="Is it running? Try: ollama serve",
            )
        except Exception as exc:
            label = step_name or description.lower().rstrip(".")
            handle_error(
                f"Error during {label}: {exc}",
                hint="Run `python main.py verify` to check your setup.",
            )


def _read_stdin() -> str:
    """Read the full job description from stdin until EOF."""
    console.print(
        "[bold cyan]Paste job description, then press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done:[/bold cyan]"
    )
    try:
        return sys.stdin.read()
    except (EOFError, KeyboardInterrupt):
        return ""


def get_job_description(file: Path | None, url: str | None) -> str:
    """Resolve a job description from *file*, *url*, or stdin.

    Args:
        file: Path to a plain-text file containing the job description.
        url: URL of a job posting to fetch and extract text from.

    Returns:
        The resolved job description string.

    Raises:
        typer.Exit: If the file cannot be read, the URL is invalid,
            or the fetched page contains fewer than 200 characters.
    """
    if file is not None:
        if not file.is_file():
            handle_error(
                f"Not a file: {file}",
                hint="Provide a valid path to a plain-text file.",
            )
        try:
            return file.read_text(encoding="utf-8")
        except OSError as exc:
            handle_error(f"Cannot read file: {exc}")

    if url is not None:
        if not url.startswith(("http://", "https://")):
            handle_error(
                f"Invalid URL: {url}",
                hint="URL must start with http:// or https://",
            )

        try:
            cleaned = fetch_url_text(url, timeout=10)
        except requests.Timeout:
            handle_error(
                f"Request to {url} timed out.",
                hint="Try again later or use --file instead.",
            )
        except requests.RequestException as exc:
            handle_error(
                f"Failed to fetch URL: {exc}",
                hint="Check the URL and your network connection.",
            )

        if len(cleaned) < 200:
            console.print(
                f"[bold yellow]Warning:[/] Extracted only {len(cleaned)} characters from the page. "
                "The job description may be hidden behind JavaScript or loaded dynamically."
            )

        return cleaned

    # Default: stdin
    return _read_stdin()


def _maybe_validate_jd(job_description: str) -> bool:
    """Validate *job_description* and ask the user whether to continue.

    Returns ``True`` if the input passes validation or the user opts to proceed
    anyway. Returns ``False`` if the user declines to continue.
    """
    is_valid, reason = validate_job_description(job_description)
    if is_valid:
        return True

    console.print(f"[bold yellow]Warning:[/] {reason}")
    try:
        proceed = typer.confirm(
            "This doesn't look like a complete job description. Continue anyway?",
            default=False,
        )
    except typer.Abort:
        return False
    return proceed


@app.callback(invoke_without_command=True)
def first_run_check(ctx: typer.Context) -> None:
    """Print a first-run hint if the resume or .env file is missing."""
    # Only run when no subcommand is given (typer prints help) or before a subcommand runs.
    # Typer invokes callback before each command; ctx.invoked_subcommand tells us which command is running.
    if ctx.invoked_subcommand is None:
        return  # User ran `python main.py` with no args; Typer will print help.

    missing: list[str] = []
    if not config.RESUME_PATH.exists():
        missing.append(f"Resume PDF not found at {config.RESUME_PATH}")
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        missing.append(f".env file not found at {env_path}")

    # Config-level warnings (non-blocking)
    config.validate_config(console)

    if missing:
        console.print(
            Panel(
                "[bold]Looks like this might be your first time running this tool.[/bold]\n\n"
                "[cyan]Step 1:[/] Copy .env.example to .env and fill in your settings\n"
                "[cyan]Step 2:[/] Place your resume PDF at resume/resume.pdf\n"
                "[cyan]Step 3:[/] Run [green]python main.py verify[/green] to confirm everything works",
                title="Welcome 👋",
                border_style="yellow",
            )
        )


@app.command()
def verify() -> None:
    """Check that the resume PDF is parseable and Ollama is reachable."""
    # Resume parseability
    if not config.RESUME_PATH.exists():
        handle_error(
            f"Resume not found at {config.RESUME_PATH}",
            hint="Place your PDF at resume/resume.pdf",
        )

    try:
        preview = preview_resume(config.RESUME_PATH, chars=300)
    except FileNotFoundError:
        handle_error(
            f"Resume not found at {config.RESUME_PATH}",
            hint="Place your PDF at resume/resume.pdf",
        )
    except ValueError:
        handle_error(
            "Could not parse resume.",
            hint="Try re-saving it as a text-based PDF.",
        )

    console.print(f"[bold green]Resume OK[/] — {preview[:120]}...")

    # Ollama reachability + model availability
    tags_url = f"{config.OLLAMA_BASE_URL}/api/tags"
    headers = {}
    if config.OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {config.OLLAMA_API_KEY}"

    try:
        resp = requests.get(tags_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        models = data.get("models", [])
        model_names = [m.get("name") or m.get("model", "") for m in models]
    except ConnectionError:
        handle_error(
            "Cannot reach Ollama.",
            hint="Is it running? Try: ollama serve",
        )
    except Exception as exc:
        handle_error(
            f"Cannot reach Ollama at {tags_url} — {exc}",
            hint="Run `python main.py verify` to check your setup.",
        )

    if config.OLLAMA_MODEL in model_names:
        console.print(
            f"[bold green]Ollama OK[/] — model [cyan]{config.OLLAMA_MODEL}[/cyan] is available."
        )
    else:
        available = ", ".join(model_names) if model_names else "(none)"
        console.print(
            f"[bold yellow]Warning:[/] Model [cyan]{config.OLLAMA_MODEL}[/cyan] not found. "
            f"Available: {available}"
        )


@app.command()
def analyze(
    file: Path | None = typer.Option(None, "--file", help="Path to a plain-text file containing the job description."),
    url: str | None = typer.Option(None, "--url", help="URL of a job posting to fetch and extract text from."),
) -> None:
    """Parse resume, prompt for a job description, and display a structured analysis."""
    resume_text = _parse_resume_for_cli()

    job_description = get_job_description(file, url)
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    if not _maybe_validate_jd(job_description):
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    result = _run_chain_with_spinner(
        "Analyzing job...",
        lambda: analyze_job(resume_text, job_description),
        step_name="analysis",
    )

    _display_analysis(result)


_SECTION_STYLES: dict[str, tuple[str, str]] = {
    "matching_skills": ("Matching Skills", "[green]✔[/green]"),
    "missing_skills": ("Missing Skills", "[red]✘[/red]"),
    "red_flags": ("Red Flags", "[yellow]⚠[/yellow]"),
    "must_have": ("Must-Have Requirements", ""),
    "nice_to_have": ("Nice-to-Have", ""),
}


def _render_bullet_table(title: str, items: list[str], icon: str = "") -> None:
    """Print a Rich table with one bullet per row.

    Args:
        title: Table title.
        items: List of strings to render as rows.
        icon: Optional icon/prefix rendered in its own column (e.g. ``[green]✔[/green]``).
    """
    table = Table(title=title, show_header=False)
    for item in items:
        if icon:
            table.add_row(icon, item)
        else:
            table.add_row(item)
    console.print(table)


def _display_analysis(result: JobAnalysis) -> None:
    """Render a JobAnalysis with Rich formatting."""
    score_color = "green" if result.match_score >= 70 else "yellow" if result.match_score >= 50 else "red"
    score_emoji = "✅" if result.match_score >= 70 else "⚠️" if result.match_score >= 50 else "❌"
    rec_color = {"apply": "green", "skip": "red", "stretch": "yellow"}.get(
        result.recommendation, "white"
    )

    console.print(
        Panel(
            f"[bold]{result.company}[/] — [italic]{result.role}[/]\n\n"
            f"Match Score: [{score_color}]{score_emoji} {result.match_score}/100[/{score_color}]\n"
            f"Recommendation: [{rec_color}]{result.recommendation}[/{rec_color}]\n\n"
            f"[bold]Summary:[/] {result.summary}",
            title="Job Analysis",
            border_style="blue",
        )
    )

    display = result.to_display_dict()
    for key, items in display.items():
        if items:
            title, icon = _SECTION_STYLES[key]
            _render_bullet_table(title, items, icon)


def _gather_inputs(file: Path | None, url: str | None) -> tuple[str, str]:
    """Parse resume and resolve job description from *file*, *url*, or stdin.

    Returns:
        A tuple of ``(resume_text, job_description)``.

    Raises:
        typer.Exit: If the resume is missing, the job description is empty,
            or validation fails and the user aborts.
    """
    resume_text = _parse_resume_for_cli()

    job_description = get_job_description(file, url)
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    if not _maybe_validate_jd(job_description):
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    return resume_text, job_description


def _run_analysis(resume_text: str, job_description: str) -> JobAnalysis:
    """Run the analyzer chain and display the results.

    Returns:
        The parsed ``JobAnalysis`` instance.
    """
    analysis = _run_chain_with_spinner(
        "Analyzing job...",
        lambda: analyze_job(resume_text, job_description),
        step_name="analysis",
    )

    _display_analysis(analysis)
    return analysis


@app.command()
def apply(
    skip_tailor: bool = typer.Option(False, "--skip-tailor", help="Skip resume tailoring."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run analysis only — no files saved, no tracker updated."),
    file: Path | None = typer.Option(None, "--file", help="Path to a plain-text file containing the job description."),
    url: str | None = typer.Option(None, "--url", help="URL of a job posting to fetch and extract text from."),
) -> None:
    """Full pipeline: analyze, optionally tailor resume, generate cover letter, save, and log."""
    from pipelines import run_apply_pipeline

    resume_text, job_description = _gather_inputs(file, url)
    analysis = _run_analysis(resume_text, job_description)

    if dry_run:
        console.print(
            Panel(
                "[bold yellow]Dry run complete[/] — no files saved and tracker not updated.",
                border_style="yellow",
            )
        )
        raise typer.Exit(0)

    try:
        cont = typer.confirm("Continue with this application?")
    except typer.Abort:
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    if not cont:
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    # Duplicate check
    if application_exists(config.TRACKER_PATH, analysis.company, analysis.role):
        console.print(
            "[bold yellow]Warning:[/] An application for this company + role "
            "already exists in the tracker."
        )

    source: str = typer.prompt(
        "Source (e.g., LinkedIn, Indeed — press Enter to skip)", default=""
    )
    notes: str = typer.prompt("Optional notes (press Enter to skip)", default="")

    result = run_apply_pipeline(
        resume_text,
        job_description,
        source=source,
        skip_tailor=skip_tailor,
        dry_run=False,
        analysis=analysis,
        notes=notes,
    )

    resume_out = result.saved_paths["resume"]
    cl_out = result.saved_paths["cover_letter"]
    console.print(
        Panel(
            f"[bold green]Application logged![/]\n\n"
            f"Tailored resume: [cyan]{resume_out}[/cyan]\n"
            f"Cover letter:    [cyan]{cl_out}[/cyan]\n"
            f"Tracker:         [cyan]{config.TRACKER_PATH}[/cyan]",
            title="Summary",
            border_style="green",
        )
    )


@app.command()
def followup(
    company: str = typer.Option(None, "--company", help="Company name."),
    role: str = typer.Option(None, "--role", help="Role title."),
    date_applied: str = typer.Option(None, "--date", help="Date applied (ISO or human-readable)."),
) -> None:
    """Draft a follow-up email. If no company is given, pick from follow-ups due in the tracker."""
    if company:
        if not role:
            role = typer.prompt("Role")
        if not date_applied:
            date_applied = typer.prompt("Date applied")
    else:
        due = get_followups_due(config.TRACKER_PATH)
        if not due:
            console.print("[yellow]No follow-ups are due today.[/]")
            raise typer.Exit(0)

        table = Table(
            title="Follow-ups Due",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("#", justify="right")
        table.add_column("Company")
        table.add_column("Role")
        table.add_column("Date Applied")
        table.add_column("Follow-up Date")

        for i, app in enumerate(due, start=1):
            table.add_row(
                str(i),
                str(app.get("Company", "")),
                str(app.get("Role", "")),
                str(app.get("Date Applied", "")),
                str(app.get("Follow-up Date", "")),
            )
        console.print(table)

        try:
            choice: int = typer.prompt("Select application by number", type=int)
        except typer.Abort:
            console.print("[yellow]Aborted.[/]")
            raise typer.Exit(0)

        if choice < 1 or choice > len(due):
            handle_error("Invalid selection.")

        selected = due[choice - 1]
        company = str(selected.get("Company", ""))
        role = str(selected.get("Role", ""))
        date_applied = str(selected.get("Date Applied", ""))

    from chains.followup import draft_followup

    email = _run_chain_with_spinner(
        "Drafting follow-up...",
        lambda: draft_followup(company, role, date_applied),
        step_name="follow-up drafting",
    )

    console.print(
        Panel(
            email,
            title=f"Follow-up for {company} — {role}",
            border_style="blue",
        )
    )

    try:
        save = typer.confirm("Save to file?")
    except typer.Abort:
        save = False

    if save:
        slug = make_slug(company, role)
        path = config.COVER_LETTERS_DIR / f"followup_{slug}"
        try:
            path.write_text(email, encoding="utf-8")
            console.print(f"[green]Saved to[/] [cyan]{path}[/cyan]")
        except OSError as exc:
            handle_error(
                f"Error saving file: {exc}",
                hint=f"Check that {config.OUTPUT_DIR} exists and is writable.",
            )


def _tracker_delete(company: str, role: str) -> None:
    """Delete an application entry after confirmation.

    Args:
        company: Company name to match.
        role: Role title to match.
    """
    if not company or not role:
        handle_error(
            "--company and --role are required with --delete.",
            hint="Example: python main.py tracker --delete --company 'Acme' --role 'Engineer'",
        )

    if not application_exists(config.TRACKER_PATH, company, role):
        handle_error(
            f"No application found for {company} — {role}.",
            hint="Run `tracker --show` to list existing entries.",
        )

    try:
        confirm = typer.confirm("Are you sure you want to delete this entry?")
    except typer.Abort:
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    if not confirm:
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    try:
        delete_application(config.TRACKER_PATH, company, role)
    except Exception as exc:
        handle_error(f"Error deleting entry: {exc}")

    console.print(
        f"[bold green]Deleted[/] application for {company} — {role}."
    )


def _tracker_edit(company: str, role: str, field: str, value: str) -> None:
    """Edit a field in an existing application entry.

    Args:
        company: Company name to match.
        role: Role title to match.
        field: Column header to update.
        value: New value for the cell.
    """
    if not company or not role:
        handle_error(
            "--company and --role are required with --edit.",
            hint="Example: python main.py tracker --edit --company 'Acme' --role 'Engineer' --field 'Notes' --value 'Had phone screen'",
        )
    if not field or not value:
        handle_error(
            "--field and --value are required with --edit.",
            hint="Example: python main.py tracker --edit --company 'Acme' --role 'Engineer' --field 'Notes' --value 'Had phone screen'",
        )

    try:
        updated = edit_application(config.TRACKER_PATH, company, role, field, value)
    except Exception as exc:
        handle_error(f"Error editing entry: {exc}")

    if not updated:
        handle_error(
            f"No application found for {company} — {role}, "
            f"or field '{field}' does not exist.",
            hint="Run `tracker --show` to list existing entries and valid fields.",
        )

    console.print(
        f"[bold green]Updated[/] {company} — {role}: {field} → [cyan]{value}[/cyan]"
    )


@app.command()
def tracker(
    show: bool = typer.Option(False, "--show", help="Display the full tracker table."),
    delete: bool = typer.Option(False, "--delete", help="Delete an application entry."),
    edit: bool = typer.Option(False, "--edit", help="Edit a field in an existing application entry."),
    company: str = typer.Option("", "--company", help="Company name (required for --delete or --edit)."),
    role: str = typer.Option("", "--role", help="Role title (required for --delete or --edit)."),
    field: str = typer.Option("", "--field", help="Field to edit (required with --edit)."),
    value: str = typer.Option("", "--value", help="New value for the field (required with --edit)."),
) -> None:
    """Show, delete, or edit entries in the application tracker."""
    if show:
        show_tracker(config.TRACKER_PATH)
        return

    if delete:
        _tracker_delete(company, role)
        return

    if edit:
        _tracker_edit(company, role, field, value)
        return

    console.print(
        "Use [cyan]tracker --show[/cyan] to display the full tracker table.\n"
        "Use [cyan]tracker --delete --company '<name>' --role '<role>'[/cyan] to delete an entry.\n"
        "Use [cyan]tracker --edit --company '<name>' --role '<role>' --field '<field>' --value '<value>'[/cyan] to edit an entry."
    )


@app.command()
def status(
    company: str = typer.Option(..., "--company", help="Company name."),
    role: str = typer.Option(..., "--role", help="Role title."),
    new_status: str = typer.Option(..., "--status", help="New status: Applied, Interviewing, Offer, Rejected, Withdrawn."),
) -> None:
    """Update the status of an existing application in the tracker."""
    try:
        update_status(config.TRACKER_PATH, company, role, new_status)
    except ValueError as exc:
        handle_error(str(exc))
    except FileNotFoundError as exc:
        handle_error(str(exc), hint="Run `python main.py apply` to create the tracker.")

    console.print(
        f"[bold green]Updated[/] {company} — {role} → [cyan]{new_status}[/cyan]"
    )


if __name__ == "__main__":
    app()
