# Interview Prep Portal - Just command runner
# Install: brew install just (macOS) or cargo install just
# Usage:   just <command>

@help:
    echo ""
    echo "  Interview Prep Portal"
    echo "  ─────────────────────────────────────────────────────────────"
    echo "  SETUP"
    echo "    just install                  Set up dependencies"
    echo ""
    echo "  PROFILE MANAGEMENT"
    echo "    just create-profile           Create profile (wizard or YAML)"
    echo "    just list-profiles            Show all profiles"
    echo "    just delete-profile <name>    Delete a profile"
    echo ""
    echo "  QUESTION GENERATION"
    echo "    just generate                 Generate questions (pick profile)"
    echo "    just generate --profile <p>   Generate for a specific profile"
    echo "    just augment                  Add questions to a topic"
    echo ""
    echo "  INTERVIEW"
    echo "    just start                    Start new interview (pick profile)"
    echo "    just start --profile <p>      Start with a specific profile"
    echo "    just resume                   Resume last incomplete session"
    echo "    just status                   Show last session status"
    echo ""
    echo "  SCORES"
    echo "    just view-scores              List score files"
    echo "    just list-sessions            Show recent sessions with scores"
    echo ""
    echo "  DEV"
    echo "    just lint                     Run ruff linter"
    echo "    just format                   Format with black"
    echo "    just clean                    Remove cache files"
    echo "  ─────────────────────────────────────────────────────────────"
    echo ""

# ── Setup ──────────────────────────────────────────────────────────────────────

install:
    uv sync
    @echo "✓ Dependencies installed"
    @echo "✓ Run 'just list-profiles' to see available profiles"
    @echo "✓ Run 'just start' to begin an interview"

# ── Profile management ─────────────────────────────────────────────────────────

create-profile *ARGS:
    uv run python main.py create-profile {{ARGS}}

list-profiles:
    uv run python main.py list-profiles

delete-profile NAME:
    uv run python main.py delete-profile {{NAME}}

# ── Question generation ────────────────────────────────────────────────────────

generate *ARGS:
    uv run python main.py generate {{ARGS}}

augment *ARGS:
    uv run python main.py augment {{ARGS}}

# ── Interview ──────────────────────────────────────────────────────────────────

start *ARGS:
    uv run python main.py start {{ARGS}}

resume:
    uv run python main.py resume

status:
    uv run python main.py status

# ── Scores & sessions ──────────────────────────────────────────────────────────

view-scores:
    #!/usr/bin/env bash
    if [ -d "scores" ] && ls scores/*.md 2>/dev/null | head -1 > /dev/null; then
        echo "Score files (newest first):"
        ls -t scores/*.md | head -10
    else
        echo "No scores yet. Complete an interview first: just start"
    fi

list-sessions:
    #!/usr/bin/env python3
    import sys
    sys.path.insert(0, '.')
    from session import Session
    sessions = Session.list_sessions()
    if not sessions:
        print('No sessions yet. Run "just start" to begin!')
    else:
        print('Recent sessions:')
        from config import SCORES_DIR
        by_mtime = sorted(sessions, key=lambda s: (SCORES_DIR / f"{s}.md").stat().st_mtime, reverse=True)
        for sid in by_mtime[:10]:
            s = Session.load(sid)
            if s:
                summary = s.get_summary()
                symbol = '✓' if s.is_complete() else '○'
                profile = s.profile_name
                print(f'  {symbol} {sid[:8]}...  profile={profile}  score={summary["overall_score"]}/100  progress={s.get_progress()}')

# ── Dev ────────────────────────────────────────────────────────────────────────

lint:
    uv run ruff check .

format:
    uv run black .

clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .ruff_cache
    @echo "✓ Cache files removed"

venv-activate:
    @echo "To activate the virtual environment:"
    @echo "  source .venv/bin/activate  (macOS/Linux)"
    @echo "  .venv\\Scripts\\activate    (Windows)"
