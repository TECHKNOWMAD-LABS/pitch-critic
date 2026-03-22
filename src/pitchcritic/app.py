"""CLI entry point for PitchCritic."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .critic import critique_pitch
from .extractor import extract_pdf
from .scorer import calculate_score

cli = typer.Typer(help="Upload your pitch deck, get it destroyed.")
console = Console()


@cli.command()
def analyze(
    pdf_path: Path = typer.Argument(..., help="Path to pitch deck PDF"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full critiques"),
) -> None:
    """Analyze a pitch deck and destroy it."""
    if not pdf_path.exists():
        typer.echo(f"Error: {pdf_path} not found", err=True)
        raise typer.Exit(1)

    console.print(f"[bold]Analyzing:[/bold] {pdf_path.name}")

    pitch_content = extract_pdf(pdf_path)
    console.print(f"Extracted {pitch_content.slide_count} slides...")

    critique = critique_pitch(pitch_content.text)
    score = calculate_score(critique)

    color = "green" if score.total >= 70 else "yellow" if score.total >= 50 else "red"
    console.print(
        Panel(
            f"[bold {color}]{score.total}/100[/bold {color}]  "
            f"Grade: {score.grade}  Verdict: {score.verdict}",
            title="Pitch Score",
        )
    )

    table = Table(title="Dimension Breakdown")
    table.add_column("Dimension", style="cyan")
    table.add_column("Score", justify="center")
    if verbose:
        table.add_column("Critique")

    for d in critique.dimensions:
        score_str = (
            f"[red]{d.score}[/red]"
            if d.score < 5
            else f"[yellow]{d.score}[/yellow]"
            if d.score < 7
            else f"[green]{d.score}[/green]"
        )
        if verbose:
            table.add_row(d.dimension, score_str, d.critique)
        else:
            table.add_row(d.dimension, score_str)

    console.print(table)
    console.print(Panel(critique.overall_verdict, title="Overall Verdict", border_style="red"))

    if score.fatal_flaws:
        console.print("\n[bold red]Fatal Flaws:[/bold red]")
        for flaw in score.fatal_flaws:
            console.print(f"  • {flaw}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
