# Just command runner for ML Interview Prep
# Install: cargo install just (or brew install just on macOS)
# Usage: just <command>

@help:
    echo "ML Interview Prep - Available Commands"
    echo "======================================"
    echo "just install    - Set up the project with dependencies"
    echo "just start      - Begin a new interview"
    echo "just resume     - Resume last incomplete interview"
    echo "just status     - Check interview progress"
    echo "just lint       - Run code linter (ruff)"
    echo "just format     - Format code with black"
    echo "just clean      - Remove cache and temp files"
    echo "just view-scores - Open the scores folder"

install:
    uv sync
    echo "✓ Setup complete! Run 'just start' to begin"

start:
    uv run python main.py start

resume:
    uv run python main.py resume

status:
    uv run python main.py status

lint:
    uv run ruff check .

format:
    uv run black .

clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .ruff_cache
    echo "✓ Cleaned up cache files"

view-scores:
    #!/usr/bin/env bash
    if [ -d "scores" ]; then
        echo "Scores folder:"
        ls -lah scores/
        echo ""
        echo "Latest score files:"
        ls -t scores/*.md 2>/dev/null | head -3
    else
        echo "No scores folder yet. Complete an interview first!"
    fi

list-sessions:
    #!/usr/bin/env python3
    from session import Session
    sessions = Session.list_sessions()
    if sessions:
        print('Available sessions:')
        for sid in reversed(sessions[-5:]):
            s = Session.load(sid)
            if s:
                summary = s.get_summary()
                status = '✓' if s.is_complete() else '○'
                print(f'  {status} {sid[:8]}... - {summary["overall_score"]}/100')
    else:
        print('No sessions yet. Run "just start" to begin!')

venv-activate:
    echo "To activate the virtual environment, run:"
    echo "  source .venv/bin/activate  (on macOS/Linux)"
    echo "  .venv\Scripts\activate    (on Windows)"
