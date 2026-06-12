"""CLI entry point for the job search tool.

Provides Typer commands: verify, analyze, apply, followup, tracker.
"""

from __future__ import annotations

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

import config
from chains.analyzer import JobAnalysis, analyze_job
from chains.cover_letter import generate_cover_letter
from chains.followup import draft_followup
from chains.tailorer import tailor_resume
from utils.helpers import make_slug
from utils.resume_parser import parse_resume, preview_resume
from utils.tracker import (
    add_application,
    application_exists,
    get_followups_due,
    show_tracker,
)

app = typer.Typer(help="Job search automation CLI.")
console = Console()


def _read_multiline_input(prompt_text: str = "Paste job description (type END on its own line to finish):") -> str:
    """Read lines from stdin until the user enters ``END`` on a blank line."""
    console.print(f"[bold cyan]{prompt_text}[/bold cyan]")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


@app.command()
def verify() -> None:
    """Check that the resume PDF is parseable and Ollama is reachable."""
    # Resume parseability
    if not config.RESUME_PATH.exists():
        console.print(f"[bold red]Error:[/] Resume not found at {config.RESUME_PATH}")
        raise typer.Exit(1)

    try:
        preview = preview_resume(config.RESUME_PATH, chars=300)
    except Exception as exc:
        console.print(f"[bold red]Error parsing resume:[/] {exc}")
        raise typer.Exit(1)

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
    except Exception as exc:
        console.print(f"[bold red]Error:[/] Cannot reach Ollama at {tags_url} — {exc}")
        raise typer.Exit(1)

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
def analyze() -> None:
    """Parse resume, prompt for a job description, and display a structured analysis."""
    if not config.RESUME_PATH.exists():
        console.print("[bold red]Error:[/] Resume not found. Run [cyan]verify[/cyan] first.")
        raise typer.Exit(1)

    with console.status("[bold green]Parsing resume..."):
        try:
            resume_text = parse_resume(config.RESUME_PATH)
        except Exception as exc:
            console.print(f"[bold red]Error parsing resume:[/] {exc}")
            raise typer.Exit(1)

    job_description = _read_multiline_input()
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Analyzing job...", total=None)
        try:
            result = analyze_job(resume_text, job_description)
        except Exception as exc:
            console.print(f"[bold red]Error during analysis:[/] {exc}")
            raise typer.Exit(1)

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
) -> None:
    """Full pipeline: analyze, optionally tailor resume, generate cover letter, save, and log."""
    if not config.RESUME_PATH.exists():
        console.print("[bold red]Error:[/] Resume not found. Run [cyan]verify[/cyan] first.")
        raise typer.Exit(1)

    with console.status("[bold green]Parsing resume..."):
        try:
            resume_text = parse_resume(config.RESUME_PATH)
        except Exception as exc:
            console.print(f"[bold red]Error parsing resume:[/] {exc}")
            raise typer.Exit(1)

    job_description = _read_multiline_input()
    if not job_description.strip():
        console.print("[yellow]No job description provided — exiting.[/]")
        raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Analyzing job...", total=None)
        try:
            analysis = analyze_job(resume_text, job_description)
        except Exception as exc:
            console.print(f"[bold red]Error during analysis:[/] {exc}")
            raise typer.Exit(1)

    _display_analysis(analysis)

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

    # Tailor resume
    if skip_tailor:
        tailored_resume = resume_text
        console.print("[yellow]Skipped resume tailoring.[/]")
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Tailoring resume...", total=None)
            try:
                tailored_resume = tailor_resume(resume_text, job_description, analysis)
            except Exception as exc:
                console.print(f"[bold red]Error tailoring resume:[/] {exc}")
                raise typer.Exit(1)

    # Generate cover letter
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Generating cover letter...", total=None)
        try:
            cover_letter = generate_cover_letter(resume_text, job_description, analysis)
        except Exception as exc:
            console.print(f"[bold red]Error generating cover letter:[/] {exc}")
            raise typer.Exit(1)

    # Save outputs
    slug = make_slug(analysis.company, analysis.role)
    resume_out = config.TAILORED_RESUMES_DIR / f"resume_{slug}"
    cl_out = config.COVER_LETTERS_DIR / f"cover_letter_{slug}"

    try:
        resume_out.write_text(tailored_resume, encoding="utf-8")
        cl_out.write_text(cover_letter, encoding="utf-8")
    except Exception as exc:
        console.print(f"[bold red]Error saving files:[/] {exc}")
        raise typer.Exit(1)

    # Optional notes
    notes: str = typer.prompt("Optional notes (press Enter to skip)", default="")

    # Update tracker
    try:
        add_application(
            path=config.TRACKER_PATH,
            company=analysis.company,
            role=analysis.role,
            source="",
            match_score=analysis.match_score,
            notes=notes,
            cover_letter_path=cl_out,
        )
    except Exception as exc:
        console.print(f"[bold red]Error updating tracker:[/] {exc}")
        raise typer.Exit(1)

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

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Drafting follow-up...", total=None)
        try:
            email = draft_followup(company, role, date_applied)
        except Exception as exc:
            console.print(f"[bold red]Error drafting follow-up:[/] {exc}")
            raise typer.Exit(1)

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
        except Exception as exc:
            console.print(f"[bold red]Error saving file:[/] {exc}")


@app.command()
def tracker(
    show: bool = typer.Option(False, "--show", help="Display the full tracker table."),
) -> None:
    """Show the application tracker."""
    if show:
        show_tracker(config.TRACKER_PATH)
    else:
        show_tracker(config.TRACKER_PATH)


if __name__ == "__main__":
    app()
