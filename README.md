# ML/Data Engineering Interview Prep Portal

A CLI-based interview preparation tool that helps candidates practice for machine learning and data engineering roles using Ollama as the evaluation backend.

## Quick Start (30 seconds)

```bash
# 1. Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install just (if you don't have it)
brew install just          # macOS
# or: cargo install just   # Any platform with Rust

# 3. Install Ollama and start it
ollama run mistral

# 4. In a new terminal, set up the project
cd ML_Interview_practice
just install

# 5. Start practicing!
just start
```

## Features

- **80 Comprehensive Questions** (16 per topic) allowing for **4+ practice attempts** without repetition:
  - Advanced Python (16 questions)
  - ML Ecosystem (16 questions)
  - Databricks (16 questions)
  - ML Fundamentals (16 questions)
  - MLOps (16 questions)

- **Randomized Question Selection**: Each interview randomly selects 15 questions with balanced representation across topics and difficulty levels

- **Mixed Question Types**:
  - Multiple Choice: Instant scoring
  - Open-Ended: LLM-powered evaluation
  - Coding Challenges: Code quality and correctness evaluation

- **Session Management**: Save progress and resume interviews (same questions)
- **Real-time Feedback**: Get detailed feedback on each answer
- **Progress Tracking**: Monitor your performance by topic
- **Local LLM Evaluation**: Uses Ollama for privacy-preserving assessment
- **Multiple Practice Attempts**: With 80 questions available, candidates can practice 4+ times with different question combinations

## Prerequisites

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

### 2. Start Ollama with a Model

```bash
ollama run mistral
```

This will download and start the Mistral model (or use an existing one). The app expects Ollama to be running on `http://localhost:11434`.

### 3. Install uv (Fast Python Package Manager)

Install `uv` from [astral.sh/uv](https://astral.sh/uv):

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use your package manager (Homebrew, pip, etc.).

### 4. Install Just (Command Runner)

Install `just` from [just.systems](https://just.systems):

```bash
# macOS
brew install just

# Linux
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.cargo/bin

# Or with Cargo (if you have Rust)
cargo install just

# Or any other method from https://just.systems/
```

## Installation

### Option 1: Quick Setup with Just (Recommended)

```bash
# Make sure Ollama is running first
ollama run mistral

# In another terminal, install just (if needed)
brew install just  # macOS
# or: cargo install just

# Then set up the project
just install
```

This will:
- Create a virtual environment with uv
- Install all dependencies
- Ready to go!

### Option 2: Manual Setup

1. Clone or navigate to this project directory

2. Ensure Ollama is running:
```bash
ollama run mistral
```

3. Install dependencies with uv:
```bash
# Install dependencies in a virtual environment
uv sync

# Or if you prefer to also install optional dev dependencies
uv sync --all-extras
```

4. Your virtual environment is now ready in `.venv/`

## Usage

### Using Just Commands (Easiest)

```bash
# Start a new interview
just start

# Resume your interview
just resume

# Check progress
just status

# View all saved scores
just view-scores

# See all available commands
just help
```

### Using uv Commands Directly

```bash
# Start a new interview
uv run python main.py start

# Resume your interview
uv run python main.py resume

# Check your status
uv run python main.py status

# Get help
uv run python main.py --help
```

### Activate Virtual Environment (Optional)

For shorter commands without `uv run`, activate the virtual environment:

```bash
# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# Now use shorter commands
python main.py start
python main.py resume
python main.py status

# Deactivate when done
deactivate
```

## Question Randomization

Each interview randomly selects 15 questions from the pool of 80 available questions:
- **Balanced by Topic**: Ensures representation across all 5 skill areas
- **Variety in Difficulty**: Mix of beginner, intermediate, and advanced questions
- **Multiple Attempts**: With 80 questions and random selection, you'll rarely see the same combination twice

Each session stores which questions were asked, so you can resume and complete the interview with the same set of questions.

## Interview Format

### Multiple Choice Questions
- You'll see 4 options (numbered 0-3)
- Enter the number of your choice
- Instant feedback on correctness

### Open-Ended Questions
- Answer with detailed explanations
- The LLM evaluator will assess your response based on:
  - Correctness and accuracy
  - Depth of understanding
  - Clarity of explanation
  - Relevant details and examples
- Press Enter twice when finished

### Coding Challenges
- You'll be given a task or problem
- Provide code (Python/pseudocode)
- Evaluation criteria:
  - Correctness
  - Code quality and readability
  - Performance and optimization
  - Best practices

## Scoring System

- **Multiple Choice**: 0 (incorrect) or 100 (correct)
- **Open-Ended**: 0-100 based on LLM evaluation
- **Coding**: 0-100 based on code quality and correctness

Your overall score is the average of all question scores.

## Session Storage

Sessions are stored in `~/.interview_prep/sessions/` as JSON files. Each session includes:
- All answers provided
- Scores for each question
- Feedback and evaluation notes
- Timestamps

You can resume any incomplete session.

## Configuration

Edit `config.py` to customize:

- `OLLAMA_HOST`: Address of Ollama server (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: LLM model to use (default: `mistral`)
- `SESSION_DIR`: Where session data is stored
- Evaluation prompts and criteria

## About uv

`uv` is a fast, modern Python package installer and resolver written in Rust. Benefits:

- **Fast**: Significantly faster than pip for dependency resolution
- **Reliable**: Deterministic dependency resolution
- **Modern**: Single tool for package management and virtual environments
- **Lock file**: `uv.lock` ensures reproducible builds across environments

### Common uv Commands

```bash
# Sync dependencies (create venv and install)
uv sync

# Add a new dependency
uv add numpy

# Add a dev dependency
uv add --dev pytest

# Update dependencies
uv update

# Run a command in the virtual environment
uv run python script.py

# Activate virtual environment for direct access
source .venv/bin/activate
```

For more information, visit [astral.sh/uv](https://astral.sh/uv)

## Troubleshooting

### "Ollama is not running"
Make sure you've started Ollama in a terminal:
```bash
ollama run mistral
```

### "Connection refused"
Check that:
1. Ollama is running
2. It's accessible at `http://localhost:11434`
3. No firewall is blocking the connection

### Slow Evaluation
LLM evaluation takes time (10-30 seconds typically). This is normal. The app is thinking deeply about your answers.

### Model Download
On first run with a model, Ollama will download it (can take a few minutes).

## Example Workflow

### Using Just Commands (Recommended)

```bash
# Set up the project (first time only)
just install

# Start a new interview
just start

# Answer all 15 questions
# ... you'll get feedback after each

# Check your results
just status

# View your saved scores in markdown
just view-scores

# Later, resume to finish if incomplete
just resume

# Or start fresh with new questions
just start
```

### Using uv Commands Directly

```bash
# Set up the project (first time only)
uv sync

# Start a new interview
uv run python main.py start

# Check your results
uv run python main.py status

# Resume to finish if incomplete
uv run python main.py resume
```

### Using Direct Python (After Activation)

```bash
# Activate environment first
source .venv/bin/activate

# Then use direct Python commands
python main.py start
python main.py status
python main.py resume

# Deactivate when done
deactivate
```

## Score Storage

Your interview scores are stored locally in the `scores/` folder as **markdown files**:

```
scores/
  ├── session-id-1.md        # Interview 1 results
  ├── session-id-2.md        # Interview 2 results
  └── session-id-3.md        # Interview 3 results
```

Each markdown file contains:
- Overall score and breakdown by topic
- Detailed feedback for each answer
- Progress tracking
- Timestamps

**View your scores:**
```bash
just view-scores              # List and open scores folder
cat scores/session-id-1.md    # View a specific score file
```

Scores are stored locally (not in cloud) so your interview data stays private.

## Tips for Preparation

1. **Take Your Time**: These aren't timed. Think deeply about your answers.
2. **Be Specific**: Provide detailed explanations and examples.
3. **Show Your Work**: For coding questions, explain your approach.
4. **Review Feedback**: Read the feedback carefully to identify weak areas.
5. **Practice Multiple Times**: Start a new session for fresh questions. With 80 total questions, you can practice 4+ times with different question combinations.
6. **Track Progress**: Use `python main.py status` to monitor your improvement across attempts.
7. **Focus on Weak Areas**: Pay special attention to topics with lower scores across multiple attempts.

## Architecture

```
main.py                - CLI interface (typer)
questions.py           - Question management
questions_data.json    - Question database (80 questions)
ollama_client.py       - Ollama API integration
evaluator.py           - Answer evaluation logic
session.py             - Session persistence (saves markdown scores)
config.py              - Configuration

pyproject.toml         - Project metadata and dependencies (uv)
justfile               - Just commands (just start, just resume, etc.)
.gitignore             - Git ignore rules

scores/                - Local folder storing interview scores as markdown files
```

## Project Files

- **pyproject.toml**: Modern Python project configuration with uv. Defines dependencies, Python version, and project metadata.
- **justfile**: Command runner using Just. Convenient commands for common tasks (install, start, resume, status, clean, view-scores, etc.)
- **scores/**: Local folder containing interview results as markdown files (stored in .gitignore)
- **requirements.txt**: Legacy format (kept for reference; use `pyproject.toml` instead)

## Notes

- All evaluation is done locally via Ollama, so your answers remain private.
- The evaluation is based on a language model (Mistral), so it may not be perfect, but provides valuable feedback.
- Questions are fixed and progressive, from beginner to advanced difficulty.
