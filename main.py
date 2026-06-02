import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from questions import QuestionBank, QuestionType
from session import Session
from evaluator import Evaluator
from ollama_client import OllamaClient

app = typer.Typer(help="Interview Preparation Portal for ML/Data Engineering roles")
console = Console()


@app.command()
def start():
    """Start a new interview session"""
    evaluator = Evaluator()
    ollama = OllamaClient()

    if not ollama.health_check():
        console.print(
            Panel(
                "[bold red]Error:[/bold red] Ollama is not running.\n"
                "Please start Ollama with: ollama run ministral\n"
                "Then try again.",
                title="Ollama Not Available",
            )
        )
        raise typer.Exit(1)

    session = Session.create_new()
    bank = QuestionBank()
    random_questions = bank.get_random_interview()
    session.set_questions(random_questions)

    console.print(
        Panel(
            "[bold green]Welcome to the ML/Data Engineering Interview Prep Portal![/bold green]\n"
            f"Total Questions: {bank.get_total_count()} (randomly selected)\n"
            "You'll be evaluated on: Python, ML Ecosystem, Databricks, ML Fundamentals, and MLOps",
            title="Interview Started",
        )
    )

    while not session.is_complete():
        question = bank.get_question(session.current_question_idx)
        if not question:
            break

        _ask_question(question, session, evaluator, bank)

    session.mark_complete()
    _show_summary(session)


@app.command()
def resume():
    """Resume the last incomplete interview"""
    session = Session.get_latest_session()

    if not session:
        console.print("[yellow]No previous session found.[/yellow]")
        raise typer.Exit(0)

    if session.is_complete():
        console.print("[yellow]Your last session is already complete.[/yellow]")
        _show_summary(session)
        raise typer.Exit(0)

    evaluator = Evaluator()
    ollama = OllamaClient()

    if not ollama.health_check():
        console.print(
            "[bold red]Error: Ollama is not running.[/bold red] "
            "Please start it and try again."
        )
        raise typer.Exit(1)

    bank = QuestionBank()

    # Reconstruct questions from session
    if session.question_ids:
        bank.questions = bank.get_by_ids(session.question_ids)

    summary = session.get_summary()

    console.print(
        Panel(
            f"[bold green]Resuming Interview[/bold green]\n"
            f"Progress: {session.get_progress()}\n"
            f"Current Score: {summary['overall_score']}/100\n"
            f"Time Elapsed: {_get_elapsed_time(session.start_time)}",
            title="Session Resumed",
        )
    )

    while not session.is_complete():
        question = bank.get_question(session.current_question_idx)
        if not question:
            break

        _ask_question(question, session, evaluator, bank)

    session.mark_complete()
    _show_summary(session)


@app.command()
def status():
    """Show the status of the current or last session"""
    session = Session.get_latest_session()

    if not session:
        console.print("[yellow]No session found.[/yellow]")
        raise typer.Exit(0)

    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)

    status_text = f"Progress: {session.get_progress()}\n"
    status_text += f"Overall Score: {summary['overall_score']}/100\n"
    status_text += f"Time Elapsed: {elapsed}\n"
    status_text += f"Status: {'Complete' if session.is_complete() else 'In Progress'}\n\n"
    status_text += "[bold]Score by Topic:[/bold]\n"

    for topic, score in summary["by_topic"].items():
        status_text += f"  {topic}: {score}/100\n"

    console.print(Panel(status_text, title="Interview Status"))


def _ask_question(question, session, evaluator, bank):
    question_num = session.current_question_idx + 1
    total = bank.get_total_count()
    progress_bar = "█" * question_num + "░" * (total - question_num)

    console.print()
    console.print(
        f"[bold cyan]Question {question_num}/{total}[/bold cyan] "
        f"[dim]({question.topic} - {question.difficulty})[/dim]\n"
        f"[dim][{progress_bar}][/dim]"
    )
    console.print(f"[bold]{question.text}[/bold]")

    if question.type == QuestionType.MULTIPLE_CHOICE:
        console.print("\n[bold green]Options:[/bold green]")
        for i, option in enumerate(question.options):
            console.print(f"  {i}: {option}")
        user_answer = typer.prompt("Your answer (0-3)")
    else:
        console.print(
            "\n[bold yellow]Provide your detailed answer (type END on a new line when done):[/bold yellow]"
        )
        user_answer = _get_multiline_input()

    # Show progress spinner while evaluating
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Evaluating your answer...", total=None)
        result = evaluator.evaluate(question, user_answer)

    session.record_answer(
        question.id,
        user_answer,
        result.score,
        result.feedback,
    )

    console.print()
    console.print(
        Panel(
            f"[bold green]Score: {result.score}/100[/bold green]\n\n"
            f"{result.feedback}\n\n"
            f"[bold green]Strengths:[/bold green]\n{result.strengths}\n\n"
            f"[bold yellow]Improvements:[/bold yellow]\n{result.improvements}",
            title="Evaluation Results",
        )
    )

    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)
    next_num = question_num + 1

    if not session.is_complete():
        console.print(
            f"[dim]Average Score: {summary['overall_score']}/100 | "
            f"Progress: {session.get_progress()} | "
            f"Elapsed: {elapsed} | "
            f"Next: Question {next_num}[/dim]"
        )
    else:
        console.print(f"[dim]Elapsed: {elapsed}[/dim]")


def _show_summary(session):
    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)

    summary_text = f"[bold green]Overall Score: {summary['overall_score']}/100[/bold green]\n\n"
    summary_text += "[bold]Score by Topic:[/bold]\n"

    for topic, score in summary["by_topic"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        summary_text += f"  {topic:20} {score:3}/100 [{bar}]\n"

    summary_text += f"\n[dim]Completed: {summary['completed']}/{summary['total_questions']} questions[/dim]"
    summary_text += f"\n[dim]Total Time: {elapsed}[/dim]"

    console.print(
        Panel(
            summary_text,
            title="[bold green]Interview Complete![/bold green]",
        )
    )

    _show_recommendations(summary)


def _show_recommendations(summary):
    console.print()
    console.print("[bold cyan]Recommended Areas to Study:[/bold cyan]")

    topics_by_score = sorted(summary["by_topic"].items(), key=lambda x: x[1])

    for topic, score in topics_by_score[:3]:
        if score < 70:
            console.print(f"  • {topic} (Score: {score}/100)")

    if all(score >= 70 for score in summary["by_topic"].values()):
        console.print("[bold green]Great job! All topics are strong![/bold green]")


def _get_multiline_input() -> str:
    """Get multi-line input from user. Type 'END' on a new line to finish."""
    lines = []
    console.print("[dim]Tip: Type END on a new line to submit[/dim]")
    try:
        while True:
            line = console.input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
    except EOFError:
        # Handle non-interactive mode
        pass
    return "\n".join(lines)


def _get_elapsed_time(start_time_str: str) -> str:
    """Calculate and format elapsed time."""
    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = datetime.now() - start
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    except Exception:
        return "N/A"


if __name__ == "__main__":
    app()
