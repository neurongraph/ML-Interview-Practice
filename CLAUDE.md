# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Install dependencies and tools
just install              # Uses uv to install deps, requires: uv, just, ollama

# Set up environment
cp .env.example .env

# Create a profile and generate questions (using local Ollama)
just create-profile       # Interactive wizard or: just create-profile --from-file profiles/my.yaml
just generate --profile <name>

# Run an interview session
just start --profile <name>

# Common dev commands
just format               # Black formatting (line-length: 100)
just lint                 # Ruff linting
just clean                # Remove cache files
```

## Project Architecture

**Purpose:** A CLI-based interview prep tool. Users define topics, generate a question bank via local LLM (Ollama), practice with randomized sessions, and get instant AI-powered feedback — all private, all local.

**Key Design:**
- **Generic:** Works for any technical role (ML, backend, systems, etc.) — profiles define topics and subtopics.
- **Local-first:** Ollama runs locally; no API keys, no remote telemetry, all data stays on disk.
- **Profile-based:** Each interview role is a profile (YAML → profile.json). Profiles contain topic definitions and generated questions.
- **Session-oriented:** Each interview session is one JSON file (for resume) + one markdown file (for human-readable score report).

### Core Modules

**main.py** — CLI entry point (Typer app)
- Commands: `create-profile`, `list-profiles`, `delete-profile`, `generate`, `augment`, `start`, `resume`, `status`, `view-scores`, `list-sessions`
- Routes to other modules; handles Ollama health check; manages user input flow for three question types (multiple-choice, open-ended, coding)

**profile_manager.py** — Profile CRUD + YAML import
- `ProfileManager` class: `list_profiles()`, `get_profile(name)`, `save_profile(config)`, `delete_profile(name)`
- Handles YAML ↔ JSON conversion
- Stores profiles in `profiles/<name>/profile.json`; questions in `profiles/<name>/questions.json` (local only, gitignored)

**question_generator.py** — LLM-based question generation
- `QuestionGenerator` class: takes a profile and generates questions via Ollama
- Prompts Ollama separately for each topic/subtopic combination, respecting difficulty/type mix (e.g., 4 beginner, 8 intermediate, 4 advanced)
- Returns list of dicts with fields: `question`, `type`, `topic`, `subtopic`, `difficulty`, `correct_answer` (for multiple-choice)

**questions.py** — Question bank + sampling
- `QuestionBank` class: loads questions from disk, provides `sample(count, topics_mix)` for random draw
- `QuestionType` enum: `MULTIPLE_CHOICE`, `OPEN_ENDED`, `CODING`
- Interview draws 15 questions per session (configurable per profile) with stratified sampling across topics

**evaluator.py** — Answer evaluation routing
- `Evaluator` class: routes to correct eval method based on question type
- Multiple-choice: instant 0/100 (binary)
- Open-ended: LLM eval via Ollama (rubric-based, 0–100)
- Coding: LLM code review via Ollama (0–100)
- All evals use prompts in `config.py` (EVALUATION_PROMPT_TEMPLATE, CODING_EVALUATION_PROMPT)

**ollama_client.py** — Ollama REST API wrapper
- `OllamaClient` class: wraps `http://localhost:11434` (configurable via `OLLAMA_HOST`)
- Methods: `health_check()`, `generate(prompt, model)`, with timeout and error handling
- Model defaults to `OLLAMA_MODEL` env var (default: `ministral-3:14b`)

**session.py** — Session persistence
- `Session` dataclass: holds `session_id`, `current_question_idx`, `answers` list, `question_ids`, `profile_name`, `start_time`, `end_time`
- Saves as two files: `scores/<id>.json` (machine-readable, for resume) + `scores/<id>.md` (human-readable report)
- Methods: `save()`, `load(session_id)`, `list_sessions()`, `get_summary()`, `get_progress()`, `is_complete()`

**config.py** — Central configuration
- Loads `.env` (Ollama host, model, timeout)
- Defines paths: `PROFILES_DIR`, `SCORES_DIR`
- Stores LLM evaluation rubrics as prompt templates

### Data Flow

1. **Profile Creation:** User provides YAML or interactive wizard → `ProfileManager.save_profile()` → `profiles/<name>/profile.json`
2. **Question Generation:** User runs `just generate --profile <name>` → `QuestionGenerator` → Ollama → `profiles/<name>/questions.json` (local only)
3. **Interview Session:** `just start --profile <name>` → `QuestionBank.sample()` → `Session` created → loop:
   - Display question
   - Get user answer
   - `Evaluator` routes to eval method
   - Save answer + score to session
   - Display feedback
4. **Session Completion:** Write `scores/<id>.md` + `scores/<id>.json`; `just resume` loads the JSON to resume

### Profile Structure (YAML → profile.json)

```yaml
name: ml-engineering
description: "ML/Data Engineering Interview Prep"
total_questions_per_interview: 15
topics:
  - name: "Python"
    subtopics: ["async/await", "decorators", "memory management"]
    question_count: 16
    difficulty_mix: {beginner: 4, intermediate: 8, advanced: 4}
    type_mix: {multiple_choice: 6, open_ended: 6, coding: 4}
```

Converts to `profiles/ml-engineering/profile.json` with identical structure. Questions generated in `profiles/ml-engineering/questions.json` (gitignored).

### Directory Layout

```
main.py, profile_manager.py, question_generator.py, questions.py, evaluator.py,
ollama_client.py, session.py, config.py          ← Core modules
pyproject.toml                                     ← uv dependencies + black/ruff config
justfile                                          ← Command runner (all user commands)
.env, .env.example                                ← Ollama config
profiles/
  template.yaml                                   ← YAML template for new profiles
  ml-engineering/
    profile.json                                  ← Profile config (committed)
    questions.json                                ← Generated questions (local only, gitignored)
  <user-profile>/
    profile.json                                  ← Same structure
    questions.json                                ← Same structure
scores/                                           ← Interview results (local only, gitignored)
  <session-id>.md                                 ← Human-readable report
  <session-id>.json                               ← Machine-readable data (for resume)
```

## Dependencies

- **typer** — CLI framework
- **requests** — HTTP client for Ollama
- **pydantic** — Data validation (used lightly in some modules)
- **rich** — Terminal UI (tables, panels, progress bars)
- **python-dotenv** — Load `.env`
- **pyyaml** — YAML parsing
- **black** (dev) — Code formatter (line-length: 100)
- **ruff** (dev) — Linter (E, F, W rules)
- **pytest** (dev) — Testing

Install with `uv sync` (installed by `just install`).

## Testing

Pytest setup exists but minimal test coverage. To add tests:

```bash
# Run tests
pytest

# Run a single test file
pytest tests/test_evaluator.py

# Run a specific test
pytest tests/test_evaluator.py::test_multiple_choice_eval
```

Tests should go in a `tests/` directory (not yet committed).

## Formatting & Linting

```bash
just format               # Black (100-char lines, py39 target)
just lint                 # Ruff (E, F, W only — no style rules)
```

Both are configured in `pyproject.toml`. Line length is 100 (not 88).

## Offline Dependency: Ollama

This tool **requires Ollama running locally**. It will not work without it:

```bash
# Ensure Ollama is installed and running
ollama serve              # Start the server (default: http://localhost:11434)
ollama pull ministral-3:14b    # Pull the default model (or any other)
```

Model can be changed via `.env` or `OLLAMA_MODEL` env var. Timeout is configurable (default: 180s, for slow hardware increase `OLLAMA_TIMEOUT`).

## Key Decisions & Gotchas

1. **Questions are local-only:** `profiles/<name>/questions.json` is gitignored. Only `profile.json` is committed. Regenerating requires Ollama.
2. **Scores are local-only:** `scores/` is gitignored. Session data (`.json`) is what allows resume; markdown is for human readability.
3. **Question sampling is deterministic per session:** Once a session starts, the 15 questions are fixed (stored in `Session.question_ids`). Resume reloads them.
4. **No persist in progress:** If you kill the CLI mid-answer, the answer is lost. Session is only saved after each complete question.
5. **Ollama health check is required:** `_require_ollama()` in main.py blocks all commands that need it (generate, start, evaluate). Fast way to catch misconfiguration early.
6. **Multi-line input uses "END" sentinel:** For open-ended and coding questions, users type `END` on its own line to submit (see `_get_multiline_input()` in main.py).

## Common Modifications

- **Change default model:** Edit `.env` → `OLLAMA_MODEL=<model>`
- **Add a new profile:** Copy `profiles/template.yaml`, edit, then run `just create-profile --from-file profiles/my.yaml`
- **Adjust question count per session:** Edit `profile.json` → `total_questions_per_interview`
- **Change scoring rubric:** Edit `EVALUATION_PROMPT_TEMPLATE` or `CODING_EVALUATION_PROMPT` in `config.py`
- **Add a new question type:** Add to `QuestionType` enum in `questions.py`, handle in `main.py` CLI loop, route eval in `evaluator.py`
