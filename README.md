# Interview Prep Portal

A CLI-based interview preparation tool that works for **any technical role**. Define your topics, generate a question bank using a local LLM (Ollama), then practice with randomised sessions and instant AI-powered feedback — all locally, all private.

## Quick Start

```bash
# 1. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install just (command runner)
brew install just          # macOS
# cargo install just       # Any platform with Rust

# 3. Install Ollama, then pull a model
brew install ollama        # macOS
ollama pull ministral-3:14b

# 4. Set up the project
git clone https://github.com/neurongraph/ML-Interview-Practice.git
cd ML-Interview-Practice
cp .env.example .env
just install

# 5. Start practising (ML/Data Engineering profile included out of the box)
just start
```

---

## What's Included

The repo ships with a ready-to-use **ML/Data Engineering** profile (80 curated questions):

| Topic | Questions |
|---|---|
| Advanced Python | 16 |
| ML Ecosystem | 16 |
| Databricks | 16 |
| ML Fundamentals | 16 |
| MLOps | 16 |

Each interview session randomly draws 15 questions (3 per topic), so you get a fresh mix every time across 4+ practice attempts.

---

## Adapting to Any Interview Role

The tool is fully generic — point it at any topics and it generates a question bank for you.

### Workflow: New Role from Scratch

```bash
# Step 1 — Create a profile (interactive wizard)
just create-profile

# Example wizard session:
#   Profile name: backend-engineer
#   Description:  Backend Engineering Interview Prep
#   Total questions per session: 15
#   Topic: Python
#     Subtopics: async/await, decorators, OOP, data structures
#     Questions to generate: 16
#   Topic: PostgreSQL
#     Subtopics: indexing, transactions, JSONB, query optimisation
#     Questions to generate: 16
#   Topic: Redis
#     Subtopics: data types, pub/sub, caching patterns, persistence
#     Questions to generate: 16
#   (Enter to finish)

# Step 2 — Generate questions (Ollama does the work, ~5-15 min)
just generate --profile backend-engineer

# Step 3 — Start practising
just start --profile backend-engineer

# Step 4 — Check your score
just status

# Later — resume if you stopped mid-session
just resume

# Want more questions on a weak topic?
just augment --profile backend-engineer --topic PostgreSQL --count 8
```

### Workflow: Profile from a YAML File

```bash
# Copy the template and edit it
cp profiles/template.yaml profiles/system-design.yaml
# edit profiles/system-design.yaml with your topics/subtopics

# Create profile from file (skips the wizard)
just create-profile --from-file profiles/system-design.yaml

# Generate questions
just generate --profile system-design

# Practice
just start --profile system-design
```

### Workflow: Adding More Questions to an Existing Topic

```bash
# Add 10 more advanced questions to a specific topic
just augment --profile ml-engineering --topic MLOps --count 10

# Or pick interactively
just augment --profile ml-engineering
#   Available topics:
#     0: Advanced Python  (16 questions)
#     1: ML Ecosystem     (16 questions)
#     2: Databricks       (16 questions)
#     3: ML Fundamentals  (16 questions)
#     4: MLOps            (16 questions)
#   Select topic (number): 4
```

---

## All Commands

```bash
# ── Setup ──────────────────────────────────────────────────────────
just install                       # Install dependencies

# ── Profile management ─────────────────────────────────────────────
just create-profile                # Wizard to create a profile
just create-profile --from-file profiles/my.yaml  # From YAML file
just list-profiles                 # Show all profiles + question counts
just delete-profile backend        # Delete a profile (asks confirmation)

# ── Question generation ────────────────────────────────────────────
just generate                      # Generate for a profile (interactive pick)
just generate --profile backend    # Generate for a specific profile
just augment                       # Add questions to a topic (interactive)
just augment --profile backend --topic Python --count 8

# ── Interview ──────────────────────────────────────────────────────
just start                         # Start new interview (pick profile if >1)
just start --profile ml-engineering  # Start with a specific profile
just resume                        # Resume last incomplete session
just status                        # Status of last session

# ── Scores ─────────────────────────────────────────────────────────
just view-scores                   # List score files
just list-sessions                 # Show recent sessions with scores

# ── Dev ────────────────────────────────────────────────────────────
just lint                          # Run ruff linter
just format                        # Format with black
just clean                         # Remove cache files
```

---

## Profile Configuration (YAML)

Profiles are stored in `profiles/<name>/profile.json`. You can also author them in YAML using the template:

```yaml
# profiles/template.yaml
name: my-profile
description: "My Interview Prep"
total_questions_per_interview: 15

topics:
  - name: "Python"
    subtopics:
      - "async/await and concurrency"
      - "decorators and metaclasses"
      - "typing and type hints"
      - "memory management"
    question_count: 16          # Questions to generate for this topic
    difficulty_mix:
      beginner: 4               # Foundational concepts
      intermediate: 8           # Applied knowledge, trade-offs
      advanced: 4               # Deep internals, architecture
    type_mix:
      multiple_choice: 6        # Instant-scored, tests breadth
      open_ended: 6             # LLM-evaluated, tests depth
      coding: 4                 # LLM-evaluated, tests implementation
```

Copy `profiles/template.yaml`, fill it in, then:
```bash
just create-profile --from-file profiles/my-profile.yaml
just generate --profile my-profile
```

---

## During an Interview

### Question Types

**Multiple Choice** — enter the option number:
```
Question 1/15 (Python · intermediate)
[█░░░░░░░░░░░░░░]

What does the `__slots__` declaration do in a Python class?

Options:
  0: Restricts attribute creation to those listed
  1: Makes all attributes read-only
  2: Automatically generates __init__
  3: Enables operator overloading

Your answer (0-3): _
```

**Open-Ended** — write as much as you need, then type `END`:
```
Question 3/15 (MLOps · advanced)
[███░░░░░░░░░░░░]

Describe your approach to detecting and handling model drift in production.

Your answer (type END on a new line when done):
Model drift occurs when...
...
END
```

**Coding** — paste or type code, then type `END`:
```
Question 7/15 (Advanced Python · intermediate)
[███████░░░░░░░░]

Write a Python decorator that retries a function up to N times on exception.

Your answer (type END on a new line when done):
def retry(n):
    def decorator(fn):
        ...
END
```

### After Each Answer

Evaluation results appear immediately:
```
┌─ Evaluation ──────────────────────────────────────────────────────┐
│ Score: 78/100                                                      │
│                                                                    │
│ Good understanding of retry logic with backoff. Missing           │
│ type hints and the delay parameter isn't configurable.            │
│                                                                    │
│ Strengths:                                                         │
│ Clean use of functools.wraps; handles exceptions correctly.       │
│                                                                    │
│ Improvements:                                                      │
│ Add configurable delay/backoff; add type annotations;             │
│ log retry attempts for observability.                             │
└───────────────────────────────────────────────────────────────────┘
Running avg: 72/100 | Progress: 7/15 | Elapsed: 14m 22s | Next: Q8
```

### Final Summary

```
┌─ Interview Complete! ─────────────────────────────────────────────┐
│ Overall Score: 74/100                                              │
│                                                                    │
│ Score by Topic:                                                    │
│   Advanced Python        82/100  [████████░░]                     │
│   ML Ecosystem           71/100  [███████░░░]                     │
│   Databricks             68/100  [██████░░░░]                     │
│   ML Fundamentals        79/100  [███████░░░]                     │
│   MLOps                  70/100  [███████░░░]                     │
│                                                                    │
│ Completed: 15/15 questions  |  Total Time: 42m 18s                │
└───────────────────────────────────────────────────────────────────┘

Recommended Areas to Study:
  • Databricks (Score: 68/100)
```

---

## Scoring System

| Question Type | Scoring |
|---|---|
| Multiple Choice | 0 (wrong) or 100 (correct) |
| Open-Ended | 0–100 via LLM rubric |
| Coding | 0–100 via LLM code review |

**LLM Rubric:**
- 90–100 Excellent — complete, accurate, well-explained with examples
- 70–89 Good — mostly correct with minor gaps
- 50–69 Fair — shows understanding but missing key details
- 30–49 Poor — incomplete or significant errors
- 0–29 Very Poor — irrelevant, incorrect, or low-effort response

---

## Configuration (.env)

```bash
cp .env.example .env
```

```env
# Ollama model (default: ministral-3:14b)
# Other options: gemma4:e4b, phi4:latest, granite4.1:8b, llama3.2:3b
OLLAMA_MODEL=ministral-3:14b

# Ollama server (default: http://localhost:11434)
# OLLAMA_HOST=http://localhost:11434

# Request timeout in seconds (default: 180)
# Increase if evaluation times out on slow hardware
# OLLAMA_TIMEOUT=180
```

---

## Project Layout

```
main.py                    CLI entry point (typer)
profile_manager.py         Profile CRUD and YAML import
question_generator.py      LLM-based question generation
questions.py               Question bank + random sampling
evaluator.py               Answer evaluation routing
ollama_client.py           Ollama REST API client
session.py                 Session persistence (.md + .json)
config.py                  Central configuration

profiles/
  template.yaml            Starter template (copy to create a profile)
  ml-engineering/
    profile.json           ML Engineering profile config
    questions.json         80 curated questions (committed)
  <your-profile>/
    profile.json           Your profile config (committed)
    questions.json         Generated questions (local only)

scores/                    Interview results as markdown (local only)
pyproject.toml             Dependencies (uv)
justfile                   Command runner (just)
.env.example               Config template
```

---

## Score Files

Each session is saved in `scores/` as a markdown file:

```
scores/
  abc12345.md        ← human-readable score report
  abc12345.json      ← machine-readable session data (for resume)
```

Score files are **local only** (`.gitignore`d). View them with:

```bash
just view-scores               # list recent files
cat scores/<session-id>.md     # open a specific report
```

---

## Prerequisites

### Ollama

Install from [ollama.ai](https://ollama.ai) then pull a model:

```bash
ollama pull ministral-3:14b    # default — good quality/speed balance
ollama pull phi4:latest        # lighter weight
ollama pull gemma4:e4b         # fast
```

The app talks to Ollama at `http://localhost:11434` by default.

### uv

Fast Python package manager — [astral.sh/uv](https://astral.sh/uv):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

### just

Command runner — [just.systems](https://just.systems):

```bash
brew install just              # macOS
cargo install just             # Rust toolchain
```

---

## Troubleshooting

### "Ollama is not running"
```bash
ollama serve                   # start the server
ollama pull ministral-3:14b    # pull the model if not present
```

### Timeout during question generation or evaluation
Increase `OLLAMA_TIMEOUT` in `.env`:
```env
OLLAMA_TIMEOUT=300
```

### Generated questions are low quality
Try a larger/smarter model:
```env
OLLAMA_MODEL=gemma4:31b-cloud
```

### Profile has no questions yet
```bash
just generate --profile <name>
```

### Resume opens wrong profile
`just resume` always loads the **most recent session**, so it'll use whichever profile was last active. To start a fresh session on a different profile:
```bash
just start --profile <name>
```
