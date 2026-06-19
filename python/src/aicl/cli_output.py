"""
Output helpers for the AICL CLI.

All terminal output goes through this module so colors, formatting, and
machine-readable (--json) mode stay consistent. Built on rich.

Usage in command handlers:
    from aicl.cli_output import out
    out.success("Compiled successfully")
    out.error("File not found: " + path)
    out.table(["Check", "Status"], [["Goal", "PASS"], ["Risk", "FAIL"]])
    out.coverage(0.95, 19, 20)
    out.section("Verification Results")
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class OutputManager:
    """Centralised CLI output with rich formatting + JSON mode.

    A single instance (`out`) is shared by all command handlers. Set
    `out.json_mode = True` to switch every method to machine-readable JSON
    on stdout (errors still go to stderr as JSON objects).
    """

    def __init__(self):
        self.console = Console()
        self.stderr_console = Console(stderr=True)
        self.json_mode = False
        self._json_buffer: List[Dict[str, Any]] = []

    # -- JSON mode ----------------------------------------------------------

    def json_emit(self, key: str, value: Any) -> None:
        """Accumulate a key-value pair for JSON output."""
        self._json_buffer.append({key: value})

    def json_flush(self) -> None:
        """Print all accumulated JSON data and clear the buffer."""
        if not self._json_buffer:
            return
        # Merge all dicts into one top-level object
        merged: Dict[str, Any] = {}
        for item in self._json_buffer:
            merged.update(item)
        print(json.dumps(merged, indent=2, default=str))
        self._json_buffer.clear()

    # -- Semantic prints ----------------------------------------------------

    def success(self, msg: str) -> None:
        """Green checkmark message."""
        if self.json_mode:
            return
        self.console.print(f"[bold green]✓[/] {msg}")

    def error(self, msg: str) -> None:
        """Red cross message (to stderr)."""
        if self.json_mode:
            print(json.dumps({"error": msg}), file=sys.stderr)
            return
        self.stderr_console.print(f"[bold red]✗[/] {msg}")

    def warning(self, msg: str) -> None:
        """Yellow warning message."""
        if self.json_mode:
            return
        self.console.print(f"[bold yellow]⚠[/] {msg}")

    def info(self, msg: str) -> None:
        """Cyan info message."""
        if self.json_mode:
            return
        self.console.print(f"[cyan]ℹ[/] {msg}")

    def print(self, msg: str = "", **kwargs) -> None:
        """Plain print (rich-formatted if string contains markup)."""
        if self.json_mode:
            return
        self.console.print(msg, **kwargs)

    def raw(self, msg: str) -> None:
        """Print without any rich markup interpretation."""
        if self.json_mode:
            return
        self.console.print(msg, markup=False, highlight=False)

    # -- Structural elements ------------------------------------------------

    def section(self, title: str) -> None:
        """A section header banner."""
        if self.json_mode:
            return
        self.console.print()
        self.console.print(f"[bold cyan]═ {title}[/]")

    def panel(self, content: str, title: str = "", style: str = "cyan") -> None:
        """A bordered panel."""
        if self.json_mode:
            return
        self.console.print(Panel(content, title=title, border_style=style))

    # -- Tables -------------------------------------------------------------

    def table(self, headers: Sequence[str], rows: Sequence[Sequence[Any]],
              title: str = "") -> None:
        """A formatted table. In JSON mode, emits as a list of dicts."""
        if self.json_mode:
            self.json_emit(title.lower().replace(" ", "_") if title else "table",
                           [dict(zip(headers, row)) for row in rows])
            return
        t = Table(title=title, show_header=True, header_style="bold cyan")
        for h in headers:
            t.add_column(h)
        for row in rows:
            t.add_row(*[str(c) for c in row])
        self.console.print(t)

    # -- Coverage -----------------------------------------------------------

    def coverage(self, pct: float, covered: int, total: int,
                 label: str = "Audit coverage") -> None:
        """Format a coverage line with color (green ≥90%, yellow ≥70%, red <70%)."""
        if self.json_mode:
            self.json_emit("coverage", {
                "label": label, "percentage": round(pct * 100, 1),
                "covered": covered, "total": total,
            })
            return
        color = "green" if pct >= 0.9 else ("yellow" if pct >= 0.7 else "red")
        bar_filled = int(pct * 20)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        self.console.print(
            f"  {label}: [{color}]{bar}[/] [{color}]{pct:.1%}[/] "
            f"({covered}/{total})"
        )

    # -- Status check line --------------------------------------------------

    def check_line(self, name: str, passed: bool, detail: str = "") -> None:
        """A PASS/FAIL check line with colored icon."""
        if self.json_mode:
            self.json_emit(name.lower().replace(" ", "_"),
                           {"status": "PASS" if passed else "FAIL", "detail": detail})
            return
        icon = "[bold green]✓[/]" if passed else "[bold red]✗[/]"
        suffix = f"  [dim]{detail}[/]" if detail else ""
        self.console.print(f"  {icon} {name}{suffix}")

    # -- Provenance ---------------------------------------------------------

    def provenance_tree(self, records: List[Any]) -> None:
        """Render provenance records as an indented tree."""
        if self.json_mode:
            self.json_emit("provenance", [
                {"type": r.source_type.value, "location": r.source_location,
                 "confidence": getattr(r, 'confidence', None)}
                for r in records
            ])
            return
        for r in records:
            stype = r.source_type.value
            color = {"ax_emission": "magenta", "sub_language": "cyan",
                     "pattern_match": "blue", "fallback": "yellow"}.get(stype, "white")
            conf = f" ({r.confidence:.0%})" if hasattr(r, 'confidence') and r.confidence else ""
            self.console.print(f"  [{color}]{stype}[/{color}] {r.source_location}{conf}")

    # -- Bare fallback ------------------------------------------------------

    def die(self, msg: str, code: int = 1) -> None:
        """Print error and exit."""
        self.error(msg)
        if self.json_mode:
            self.json_flush()
        sys.exit(code)


# Singleton — import as `from aicl.cli_output import out`
out = OutputManager()
