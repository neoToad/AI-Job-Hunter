"""CLI entry point for the job search tool.

Provides Typer commands: verify, analyze, apply, followup, tracker.
"""

from __future__ import annotations

import sys
from pathlib import Path

import asyncio
import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

import config
from chains.analyzer import JobAnalysis
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
        console.print(f"[bold red]Error:[/] Resume not found at {config.RESUME_PATH}")
        raise typer.Exit(1)

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
    if not config.RESUME_PATH.exists():
        console.print("[bold red]Error:[/] Resume not found. Run [cyan]verify[/cyan] first.")
        raise typer.Exit(1)

    with console.status("[bold green]Parsing resume..."):
        try:
            resume_text = get_resume_text(config.RESUME_PATH)
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

    job_description = get_job_description(file, url)
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    from chains.analyzer import analyze_job, validate_job_description

    if not _maybe_validate_jd(job_description):
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Analyzing job...", total=None)
        try:
            result = analyze_job(resume_text, job_description)
        except ConnectionError:
            handle_error(
                "Cannot reach Ollama.",
                hint="Is it running? Try: ollama serve",
            )
        except Exception as exc:
            handle_error(
                f"Error during analysis: {exc}",
                hint="Run `python main.py verify` to check your setup.",
            )

    _display_analysis(result)


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

    if result.matching_skills:
        table = Table(title="Matching Skills", show_header=False)
        for skill in result.matching_skills:
            table.add_row("[green]✔[/green]", skill)
        console.print(table)

    if result.missing_skills:
        table = Table(title="Missing Skills", show_header=False)
        for skill in result.missing_skills:
            table.add_row("[red]✘[/red]", skill)
        console.print(table)

    if result.red_flags:
        table = Table(title="Red Flags", show_header=False)
        for flag in result.red_flags:
            table.add_row("[yellow]⚠[/yellow]", flag)
        console.print(table)

    if result.must_have:
        table = Table(title="Must-Have Requirements", show_header=False)
        for req in result.must_have:
            table.add_row(req)
        console.print(table)

    if result.nice_to_have:
        table = Table(title="Nice-to-Have", show_header=False)
        for req in result.nice_to_have:
            table.add_row(req)
        console.print(table)


@app.command()
def apply(
    skip_tailor: bool = typer.Option(False, "--skip-tailor", help="Skip resume tailoring."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run analysis only — no files saved, no tracker updated."),
    file: Path | None = typer.Option(None, "--file", help="Path to a plain-text file containing the job description."),
    url: str | None = typer.Option(None, "--url", help="URL of a job posting to fetch and extract text from."),
) -> None:
    """Full pipeline: analyze, optionally tailor resume, generate cover letter, save, and log."""
    if not config.RESUME_PATH.exists():
        console.print("[bold red]Error:[/] Resume not found. Run [cyan]verify[/cyan] first.")
        raise typer.Exit(1)

    with console.status("[bold green]Parsing resume..."):
        try:
            resume_text = get_resume_text(config.RESUME_PATH)
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

    job_description = get_job_description(file, url)
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    from chains.analyzer import analyze_job, validate_job_description

    if not _maybe_validate_jd(job_description):
        console.print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Analyzing job...", total=None)
        try:
            analysis = analyze_job(resume_text, job_description)
        except ConnectionError:
            handle_error(
                "Cannot reach Ollama.",
                hint="Is it running? Try: ollama serve",
            )
        except Exception as exc:
            handle_error(
                f"Error during analysis: {exc}",
                hint="Run `python main.py verify` to check your setup.",
            )

    _display_analysis(analysis)

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

    from chains.tailorer import tailor_resume
    from chains.cover_letter import generate_cover_letter

    # Tailor resume and generate cover letter concurrently
    if skip_tailor:
        tailored_resume = resume_text
        console.print("[yellow]Skipped resume tailoring.[/]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Generating cover letter...", total=None)
            try:
                cover_letter = generate_cover_letter(resume_text, job_description, analysis)
            except ConnectionError:
                handle_error(
                    "Cannot reach Ollama.",
                    hint="Is it running? Try: ollama serve",
                )
            except Exception as exc:
                handle_error(
                    f"Error generating cover letter: {exc}",
                    hint="Run `python main.py verify` to check your setup.",
                )
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(
                description="Tailoring resume & generating cover letter...", total=None
            )
            try:

                async def _tailor_and_cover():
                    return await asyncio.gather(
                        asyncio.to_thread(
                            tailor_resume, resume_text, job_description, analysis
                        ),
                        asyncio.to_thread(
                            generate_cover_letter, resume_text, job_description, analysis
                        ),
                    )

                tailored_resume, cover_letter = asyncio.run(_tailor_and_cover())
            except ConnectionError:
                handle_error(
                    "Cannot reach Ollama.",
                    hint="Is it running? Try: ollama serve",
                )
            except Exception as exc:
                handle_error(
                    f"Error during tailoring or cover letter generation: {exc}",
                    hint="Run `python main.py verify` to check your setup.",
                )

    # Save outputs
    slug = make_slug(analysis.company, analysis.role)
    resume_out = config.TAILORED_RESUMES_DIR / f"resume_{slug}"
    cl_out = config.COVER_LETTERS_DIR / f"cover_letter_{slug}"

    try:
        resume_out.write_text(tailored_resume, encoding="utf-8")
        cl_out.write_text(cover_letter, encoding="utf-8")
    except OSError as exc:
        handle_error(
            f"Error saving files: {exc}",
            hint=f"Check that {config.OUTPUT_DIR} exists and is writable.",
        )

    # Optional source and notes
    source: str = typer.prompt("Source (e.g., LinkedIn, Indeed — press Enter to skip)", default="")
    notes: str = typer.prompt("Optional notes (press Enter to skip)", default="")

    # Update tracker
    try:
        add_application(
            path=config.TRACKER_PATH,
            company=analysis.company,
            role=analysis.role,
            source=source,
            match_score=analysis.match_score,
            notes=notes,
            cover_letter_path=cl_out,
        )
    except Exception as exc:
        handle_error(
            f"Error updating tracker: {exc}",
            hint="Run `python main.py verify` to check your setup.",
        )

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
            console.print("[bold red]Invalid selection.[/]")
            raise typer.Exit(1)

        selected = due[choice - 1]
        company = str(selected.get("Company", ""))
        role = str(selected.get("Role", ""))
        date_applied = str(selected.get("Date Applied", ""))

    from chains.followup import draft_followup

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Drafting follow-up...", total=None)
        try:
            email = draft_followup(company, role, date_applied)
        except ConnectionError:
            handle_error(
                "Cannot reach Ollama.",
                hint="Is it running? Try: ollama serve",
            )
        except Exception as exc:
            handle_error(
                f"Error drafting follow-up: {exc}",
                hint="Run `python main.py verify` to check your setup.",
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
        if not company or not role:
            handle_error(
                "--company and --role are required with --delete.",
                hint="Example: python main.py tracker --delete --company 'Acme' --role 'Engineer'",
            )
        if not application_exists(config.TRACKER_PATH, company, role):
            console.print(
                f"[bold yellow]No application found for {company} — {role}.[/]"
            )
            raise typer.Exit(1)

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
        return

    if edit:
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
            console.print(
                f"[bold yellow]No application found for {company} — {role}, "
                f"or field '{field}' does not exist.[/]"
            )
            raise typer.Exit(1)

        console.print(
            f"[bold green]Updated[/] {company} — {role}: {field} → [cyan]{value}[/cyan]"
        )
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
