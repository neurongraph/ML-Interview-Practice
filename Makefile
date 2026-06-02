.PHONY: help install start resume status clean lint format test

help:
	@echo "ML Interview Prep - Available Commands"
	@echo "======================================"
	@echo "make install    - Set up the project with dependencies"
	@echo "make start      - Begin a new interview"
	@echo "make resume     - Resume last incomplete interview"
	@echo "make status     - Check interview progress"
	@echo "make lint       - Run code linter"
	@echo "make format     - Format code with black"
	@echo "make clean      - Remove cache and temp files"

install:
	uv sync
	@echo "✓ Setup complete! Run 'make start' to begin"

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
	@echo "✓ Cleaned up cache files"

venv-activate:
	@echo "To activate the virtual environment, run:"
	@echo "  source .venv/bin/activate  (on macOS/Linux)"
	@echo "  .venv\\Scripts\\activate    (on Windows)"
