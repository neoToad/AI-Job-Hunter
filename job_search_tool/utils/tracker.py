"""Application tracker backed by an Excel workbook (openpyxl).

Provides CRUD-style helpers for logging job applications, detecting duplicates,
and surfacing follow-ups that are due.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from rich.console import Console
from rich.table import Table

_HEADERS = [
    "Company",
    "Role",
    "Date Applied",
    "Source",
    "Match Score",
    "Status",
    "Follow-up Date",
    "Notes",
    "Cover Letter Path",
]


def _get_or_create_workbook(path: Path) -> Workbook:
    """Load an existing workbook or create a new one with bold headers.

    Args:
        path: Path to the .xlsx tracker file.

    Returns:
        An openpyxl Workbook instance (loaded or freshly created).
    """
    if path.exists():
        try:
            wb = load_workbook(path)
            ws = wb.active
            # Ensure headers are present; if sheet is empty or malformed, recreate.
            if ws is None or ws.max_row == 0:
                raise ValueError("Empty worksheet")
            return wb
        except Exception:
            wb = Workbook()
            ws = wb.active
            ws.title = "Applications"
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Applications"

    ws.append(_HEADERS)
    bold = Font(bold=True)
    for cell in ws[1]:
        cell.font = bold
    return wb


def application_exists(path: Path, company: str, role: str) -> bool:
    """Return True if an application for the same *company* + *role*
    (case-insensitive, stripped) already exists in the tracker.

    Args:
        path: Path to the .xlsx tracker file.
        company: Company name.
        role: Job role/title.

    Returns:
        Boolean indicating whether a duplicate entry was found.
    """
    if not path.exists():
        return False

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        return False

    target_company = company.strip().lower()
    target_role = role.strip().lower()

    # Skip header row
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) < 2:
            continue
        if str(row[0] or "").strip().lower() == target_company and str(
            row[1] or ""
        ).strip().lower() == target_role:
            return True
    return False


def add_application(
    path: Path,
    company: str,
    role: str,
    source: str,
    match_score: float | int | str,
    notes: str,
    cover_letter_path: str | Path,
) -> None:
    """Append a new application row to the tracker.

    Auto-fills:
    - *Date Applied* → today's date (ISO format).
    - *Status* → ``"Applied"``.
    - *Follow-up Date* → 14 days from today.

    Args:
        path: Path to the .xlsx tracker file.
        company: Company name.
        role: Job role/title.
        source: Where the posting was found (e.g. LinkedIn, Indeed).
        match_score: Numerical or string match score.
        notes: Free-text notes.
        cover_letter_path: Path to the generated cover letter.
    """
    wb = _get_or_create_workbook(path)
    ws = wb.active
    today = date.today()
    follow_up = today + timedelta(days=14)

    ws.append(
        [
            company,
            role,
            today.isoformat(),
            source,
            str(match_score),
            "Applied",
            follow_up.isoformat(),
            notes,
            str(cover_letter_path),
        ]
    )
    wb.save(path)


def show_tracker(path: Path) -> None:
    """Print every row in the tracker as a formatted Rich table.

    Args:
        path: Path to the .xlsx tracker file.
    """
    if not path.exists():
        print(f"Tracker not found: {path}")
        return

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        print("Tracker workbook has no active sheet.")
        return

    table = Table(title="Job Application Tracker", show_header=True, header_style="bold magenta")
    for header in _HEADERS:
        table.add_column(header)

    for row in ws.iter_rows(values_only=True):
        # Render every cell as a string; empty cells become ""
        table.add_row(*(str(cell or "") for cell in row))

    console = Console()
    console.print(table)


def get_followups_due(path: Path) -> list[dict[str, Any]]:
    """Return applications whose Status is ``"Applied"`` and whose
    Follow-up Date is today or earlier.

    Args:
        path: Path to the .xlsx tracker file.

    Returns:
        List of application rows as dictionaries keyed by column header.
    """
    if not path.exists():
        return []

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        return []

    today = date.today()
    due: list[dict[str, Any]] = []

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [str(h or f"Col{i}") for i, h in enumerate(rows[0])]
    for row in rows[1:]:
        row_dict = dict(zip(headers, row))
        status = str(row_dict.get("Status", "")).strip()
        follow_up_raw = row_dict.get("Follow-up Date", "")
        try:
            follow_up = date.fromisoformat(str(follow_up_raw).strip())
        except (ValueError, TypeError):
            continue

        if status == "Applied" and follow_up <= today:
            due.append(row_dict)

    return due