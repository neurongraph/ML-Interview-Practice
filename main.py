from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config import DEFAULT_PROFILE, PROFILES_DIR
from evaluator import Evaluator
from ollama_client import OllamaClient
from profile_manager import ProfileManager
from question_generator import QuestionGenerator
from questions import QuestionBank, QuestionType
from session import Session

app = typer.Typer(
    help="Interview Prep Portal — practice for any technical interview using a local LLM.",
    no_args_is_help=True,
)
console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _get_manager() -> ProfileManager:
    return ProfileManager(PROFILES_DIR)


def _select_profile(profiles: List[str], prompt_text: str) -> str:
    """Interactive numbered profile picker."""
    console.print(f"\n[bold]{prompt_text}:[/bold]")
    for i, name in enumerate(profiles):
        console.print(f"  [cyan]{i}[/cyan]: {name}")
    while True:
        raw = typer.prompt("Enter number")
        try:
            choice = int(raw)
            if 0 <= choice < len(profiles):
                return profiles[choice]
        except ValueError:
            pass
        console.print("[yellow]Invalid choice, try again.[/yellow]")


def _require_ollama() -> OllamaClient:
    client = OllamaClient()
    if not client.health_check():
        console.print(
            Panel(
                "[bold red]Ollama is not running.[/bold red]\n"
                "Start it with:  ollama serve\n"
                "Then pull a model:  ollama pull ministral-3:14b",
                title="Ollama Unavailable",
            )
        )
        raise typer.Exit(1)
    return client


def _get_elapsed_time(start_time_str: str) -> str:
    try:
        start = datetime.fromisoformat(start_time_str)
        elapsed = datetime.now() - start
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    except Exception:
        return "N/A"


def _get_multiline_input() -> str:
    """Multi-line input; type END on its own line to submit."""
    lines = []
    console.print("[dim]Tip: Type END on a new line to submit[/dim]")
    try:
        while True:
            line = console.input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def _resolve_profile(manager: ProfileManager, profile: Optional[str]) -> str:
    """Return a valid profile name, prompting the user if needed."""
    profiles = manager.list_profiles()
    if not profiles:
        console.print(
            "[red]No profiles found.[/red] "
            "Create one with:  just create-profile"
        )
        raise typer.Exit(1)

    if profile:
        if profile not in profiles:
            console.print(f"[red]Profile '{profile}' not found.[/red]")
            console.print(f"Available: {', '.join(profiles)}")
            raise typer.Exit(1)
        return profile

    if len(profiles) == 1:
        return profiles[0]

    return _select_profile(profiles, "Select interview profile")


# ═══════════════════════════════════════════════════════════════════════════════
# Profile Management Commands
# ═══════════════════════════════════════════════════════════════════════════════

@app.command("create-profile")
def create_profile(
    from_file: Optional[Path] = typer.Option(
        None, "--from-file", "-f",
        help="Path to a YAML profile config (skips the wizard)",
    ),
):
    """Create a new interview profile — wizard or from a YAML file."""
    manager = _get_manager()

    if from_file:
        if not from_file.exists():
            console.print(f"[red]File not found: {from_file}[/red]")
            raise typer.Exit(1)
        config = manager.load_from_yaml(from_file)
        console.print(f"[green]Loaded profile config from {from_file}[/green]")
    else:
        # ── Interactive wizard ──────────────────────────────────────────────
        console.print(
            Panel(
                "[bold]Create a new Interview Profile[/bold]\n"
                "Answer the prompts below. You can also skip the wizard by\n"
                "copying [cyan]profiles/template.yaml[/cyan] and running:\n"
                "  [bold]just create-profile --from-file profiles/my-profile.yaml[/bold]",
                title="Profile Wizard",
            )
        )

        raw_name = typer.prompt("\nProfile name (e.g. backend-engineer)")
        name = raw_name.lower().replace(" ", "-")
        description = typer.prompt(
            "Description",
            default=f"{name.replace('-', ' ').title()} Interview Prep",
        )
        total_q = int(typer.prompt("Total questions per interview session", default="15"))

        topics = []
        console.print("\n[bold]Define topics[/bold] (press Enter with an empty name to finish):")

        while True:
            topic_name = typer.prompt("\n  Topic name (or Enter to finish)", default="")
            if not topic_name.strip():
                if not topics:
                    console.print("[yellow]  At least one topic is required.[/yellow]")
                    continue
                break

            subtopics_raw = typer.prompt(f"  Subtopics for '{topic_name}' (comma-separated)")
            subtopics = [s.strip() for s in subtopics_raw.split(",") if s.strip()]
            q_count = int(typer.prompt(f"  Questions to generate for '{topic_name}'", default="16"))

            topics.append(
                {
                    "name": topic_name,
                    "subtopics": subtopics,
                    "question_count": q_count,
                    "difficulty_mix": {"beginner": 4, "intermediate": 8, "advanced": 4},
                    "type_mix": {"multiple_choice": 6, "open_ended": 6, "coding": 4},
                }
            )
            console.print(f"  [green]✓ Added: {topic_name}[/green]")

        config = {
            "name": name,
            "description": description,
            "total_questions_per_interview": total_q,
            "topics": topics,
        }

    # ── Save ────────────────────────────────────────────────────────────────
    profile_dir = manager.save_profile(config)
    console.print(
        Panel(
            f"[bold green]✓ Profile '{config['name']}' created![/bold green]\n\n"
            f"Config saved to:  {profile_dir}/profile.json\n\n"
            f"Next — generate questions:\n"
            f"  [bold]just generate --profile {config['name']}[/bold]",
            title="Profile Created",
        )
    )


@app.command("list-profiles")
def list_profiles():
    """List all available interview profiles."""
    manager = _get_manager()
    profiles = manager.list_profiles()

    if not profiles:
        console.print(
            "[yellow]No profiles found.[/yellow] "
            "Create one with:  just create-profile"
        )
        return

    table = Table(title="Interview Profiles", show_lines=True)
    table.add_column("Profile", style="bold cyan")
    table.add_column("Description")
    table.add_column("Topics")
    table.add_column("Questions in Pool", justify="right")
    table.add_column("Per Session", justify="right")

    for name in profiles:
        cfg = manager.get_profile(name) or {}
        topics = ", ".join(t["name"] for t in cfg.get("topics", []))
        q_count = manager.get_question_count(name)
        per_session = cfg.get("total_questions_per_interview", 15)
        table.add_row(name, cfg.get("description", ""), topics, str(q_count), str(per_session))

    console.print(table)


@app.command("delete-profile")
def delete_profile(
    name: Optional[str] = typer.Argument(None, help="Profile name to delete"),
):
    """Delete an interview profile and all its questions."""
    manager = _get_manager()

    if not name:
        profiles = manager.list_profiles()
        if not profiles:
            console.print("[yellow]No profiles to delete.[/yellow]")
            return
        name = _select_profile(profiles, "Select profile to delete")

    confirmed = typer.confirm(
        f"\n[bold red]Delete profile '{name}'?[/bold red] "
        "This removes the profile config AND all generated questions. Cannot be undone.",
        default=False,
    )
    if not confirmed:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    if manager.delete_profile(name):
        console.print(f"[green]✓ Profile '{name}' deleted.[/green]")
    else:
        console.print(f"[red]Profile '{name}' not found.[/red]")


# ═══════════════════════════════════════════════════════════════════════════════
# Question Generation Commands
# ═══════════════════════════════════════════════════════════════════════════════

@app.command()
def generate(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile name"),
):
    """Generate questions for a profile using the local LLM (Ollama)."""
    manager = _get_manager()
    profile = _resolve_profile(manager, profile)
    cfg = manager.get_profile(profile)
    _require_ollama()

    topics_str = ", ".join(t["name"] for t in cfg.get("topics", []))
    total_to_generate = sum(t.get("question_count", 16) for t in cfg.get("topics", []))
    existing = manager.get_question_count(profile)

    console.print(
        Panel(
            f"[bold]Generating questions for:[/bold] {profile}\n"
            f"Topics: {topics_str}\n"
            f"Target questions: ~{total_to_generate}  |  Already in pool: {existing}\n\n"
            f"[dim]Each batch calls Ollama — this typically takes 5-15 minutes.[/dim]",
            title="Question Generation",
        )
    )

    generator = QuestionGenerator()
    questions_path = manager.get_questions_path(profile)
    new_count = generator.generate_for_profile(cfg, questions_path)
    total = manager.get_question_count(profile)

    console.print(
        Panel(
            f"[bold green]✓ Generated {new_count} new questions![/bold green]\n"
            f"Total pool: {total} questions\n\n"
            f"Start an interview:\n"
            f"  [bold]just start --profile {profile}[/bold]",
            title="Done",
        )
    )


@app.command()
def augment(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile name"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Topic to augment"),
    count: int = typer.Option(8, "--count", "-n", help="Number of new questions to add"),
):
    """Add more questions to a specific topic in a profile."""
    manager = _get_manager()
    profile = _resolve_profile(manager, profile)
    cfg = manager.get_profile(profile)
    _require_ollama()

    topic_names = [t["name"] for t in cfg.get("topics", [])]
    if not topic:
        console.print("\n[bold]Available topics:[/bold]")
        for i, t in enumerate(topic_names):
            counts = manager.get_topic_question_counts(profile)
            console.print(f"  [cyan]{i}[/cyan]: {t}  ({counts.get(t, 0)} questions)")
        while True:
            raw = typer.prompt("Select topic (number)")
            try:
                idx = int(raw)
                if 0 <= idx < len(topic_names):
                    topic = topic_names[idx]
                    break
            except ValueError:
                pass
            console.print("[yellow]Invalid choice.[/yellow]")

    if topic not in topic_names:
        console.print(f"[red]Topic '{topic}' not in profile '{profile}'.[/red]")
        raise typer.Exit(1)

    before = manager.get_topic_question_counts(profile).get(topic, 0)
    console.print(
        Panel(
            f"[bold]Augmenting:[/bold] {topic}  (in profile: {profile})\n"
            f"Existing questions for this topic: {before}\n"
            f"Generating: ~{count} new questions",
            title="Topic Augmentation",
        )
    )

    generator = QuestionGenerator()
    questions_path = manager.get_questions_path(profile)
    new_count = generator.generate_for_profile(cfg, questions_path, augment_topic=topic, augment_count=count)
    after = manager.get_topic_question_counts(profile).get(topic, 0)

    console.print(
        f"\n[bold green]✓ Added {new_count} questions to '{topic}'[/bold green]\n"
        f"  {topic}: {before} → {after} questions  |  "
        f"Pool total: {manager.get_question_count(profile)}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Interview Commands
# ═══════════════════════════════════════════════════════════════════════════════

@app.command()
def start(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to interview with"),
):
    """Start a new interview session."""
    manager = _get_manager()
    profile = _resolve_profile(manager, profile)
    cfg = manager.get_profile(profile)

    if manager.get_question_count(profile) == 0:
        console.print(
            f"[red]No questions found for profile '{profile}'.[/red]\n"
            f"Generate them first:  just generate --profile {profile}"
        )
        raise typer.Exit(1)

    _require_ollama()
    evaluator = Evaluator()

    session = Session.create_new(profile_name=profile)
    bank = QuestionBank(profile_name=profile)
    questions = bank.get_random_interview()
    session.set_questions(questions)

    topics_str = ", ".join(t["name"] for t in cfg.get("topics", []))
    console.print(
        Panel(
            f"[bold green]Welcome to the Interview Prep Portal![/bold green]\n\n"
            f"Profile:   {cfg.get('description', profile)}\n"
            f"Topics:    {topics_str}\n"
            f"Questions: {bank.get_pool_size()} in pool → {len(questions)} selected for this session\n\n"
            f"[dim]Type END on a new line to submit open-ended answers.[/dim]",
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
    """Resume the last incomplete interview session."""
    session = Session.get_latest_session()

    if not session:
        console.print("[yellow]No previous session found.[/yellow]")
        raise typer.Exit(0)

    if session.is_complete():
        console.print("[yellow]Your last session is already complete.[/yellow]")
        _show_summary(session)
        raise typer.Exit(0)

    _require_ollama()
    evaluator = Evaluator()

    bank = QuestionBank(profile_name=session.profile_name)
    if session.question_ids:
        bank.questions = bank.get_by_ids(session.question_ids)

    summary = session.get_summary()
    console.print(
        Panel(
            f"[bold green]Resuming Interview[/bold green]\n\n"
            f"Profile:  {session.profile_name}\n"
            f"Progress: {session.get_progress()}\n"
            f"Score so far: {summary['overall_score']}/100\n"
            f"Elapsed: {_get_elapsed_time(session.start_time)}",
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
    """Show the status of the last interview session."""
    session = Session.get_latest_session()

    if not session:
        console.print("[yellow]No session found. Run 'just start' to begin![/yellow]")
        raise typer.Exit(0)

    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)

    text = (
        f"Profile:  {session.profile_name}\n"
        f"Progress: {session.get_progress()}\n"
        f"Score:    {summary['overall_score']}/100\n"
        f"Elapsed:  {elapsed}\n"
        f"Status:   {'✓ Complete' if session.is_complete() else '○ In Progress'}\n\n"
        "[bold]Score by Topic:[/bold]\n"
    )
    for topic, score in summary["by_topic"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        text += f"  {topic:25} {score:3}/100  [{bar}]\n"

    console.print(Panel(text, title="Interview Status"))


# ═══════════════════════════════════════════════════════════════════════════════
# Internal interview helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _ask_question(question, session, evaluator, bank):
    question_num = session.current_question_idx + 1
    total = bank.get_total_count()
    progress_bar = "█" * question_num + "░" * (total - question_num)

    console.print()
    console.print(
        f"[bold cyan]Question {question_num}/{total}[/bold cyan] "
        f"[dim]({question.topic} · {question.difficulty})[/dim]\n"
        f"[dim][{progress_bar}][/dim]"
    )
    console.print(f"\n[bold]{question.text}[/bold]")

    if question.type == QuestionType.MULTIPLE_CHOICE:
        console.print("\n[bold green]Options:[/bold green]")
        for i, opt in enumerate(question.options):
            console.print(f"  [cyan]{i}[/cyan]: {opt}")
        user_answer = typer.prompt("Your answer (0-3)")
    else:
        console.print(
            "\n[bold yellow]Your answer (type END on a new line when done):[/bold yellow]"
        )
        user_answer = _get_multiline_input()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Evaluating your answer...", total=None)
        result = evaluator.evaluate(question, user_answer)

    session.record_answer(question.id, user_answer, result.score, result.feedback)

    console.print()
    console.print(
        Panel(
            f"[bold green]Score: {result.score}/100[/bold green]\n\n"
            f"{result.feedback}\n\n"
            f"[bold green]Strengths:[/bold green]\n{result.strengths}\n\n"
            f"[bold yellow]Improvements:[/bold yellow]\n{result.improvements}",
            title="Evaluation",
        )
    )

    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)

    if not session.is_complete():
        console.print(
            f"[dim]Running avg: {summary['overall_score']}/100 | "
            f"Progress: {session.get_progress()} | "
            f"Elapsed: {elapsed} | "
            f"Next: Q{question_num + 1}[/dim]"
        )
    else:
        console.print(f"[dim]Elapsed: {elapsed}[/dim]")


def _show_summary(session: Session):
    summary = session.get_summary()
    elapsed = _get_elapsed_time(session.start_time)

    text = f"[bold green]Overall Score: {summary['overall_score']}/100[/bold green]\n\n"
    text += "[bold]Score by Topic:[/bold]\n"
    for topic, score in summary["by_topic"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        text += f"  {topic:25} {score:3}/100  [{bar}]\n"
    text += f"\n[dim]Completed: {summary['completed']}/{summary['total_questions']} questions[/dim]"
    text += f"\n[dim]Total Time: {elapsed}[/dim]"

    console.print(Panel(text, title="[bold green]Interview Complete![/bold green]"))

    # Recommendations
    weak = [(t, s) for t, s in summary["by_topic"].items() if s < 70]
    if weak:
        console.print("\n[bold cyan]Recommended Areas to Study:[/bold cyan]")
        for topic, score in sorted(weak, key=lambda x: x[1]):
            console.print(f"  • {topic} (Score: {score}/100)")
    else:
        console.print("\n[bold green]Great job! All topics scored 70+.[/bold green]")


if __name__ == "__main__":
    app()
