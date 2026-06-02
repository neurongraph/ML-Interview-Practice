# Contributing to ML Interview Prep

Thank you for your interest in contributing! Here's how you can help.

## Adding New Questions

Questions are stored in `questions_data.json`. To add new questions:

1. Open `questions_data.json`
2. Add a new question object to the `"questions"` array with this structure:

```json
{
  "id": 81,
  "topic": "Advanced Python",
  "difficulty": "intermediate",
  "type": "multiple_choice",
  "text": "Your question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "evaluation_criteria": "What the LLM should evaluate"
}
```

### Question Structure

- **id**: Unique integer (must be unique)
- **topic**: One of: "Advanced Python", "ML Ecosystem", "Databricks", "ML Fundamentals", "MLOps"
- **difficulty**: "beginner", "intermediate", or "advanced"
- **type**: "multiple_choice", "open_ended", or "coding"
- **text**: The question text (use \n for line breaks in code)
- **evaluation_criteria**: What to evaluate (for LLM-based scoring)
- **options**: Array of 4 strings (required for multiple_choice)
- **correct_answer**: Index of correct option (0-3, required for multiple_choice)

### Question Type Examples

**Multiple Choice:**
```json
{
  "id": 81,
  "topic": "Advanced Python",
  "difficulty": "beginner",
  "type": "multiple_choice",
  "text": "What is X?",
  "options": ["Answer A", "Answer B", "Answer C", "Answer D"],
  "correct_answer": 1,
  "evaluation_criteria": "Understanding of X"
}
```

**Open-Ended:**
```json
{
  "id": 82,
  "topic": "ML Ecosystem",
  "difficulty": "intermediate",
  "type": "open_ended",
  "text": "Explain how you would approach Y?",
  "evaluation_criteria": "Deep understanding of approach, best practices, trade-offs"
}
```

**Coding Challenge:**
```json
{
  "id": 83,
  "topic": "Databricks",
  "difficulty": "advanced",
  "type": "coding",
  "text": "Write code to do Z:\n\n```python\n# Your task here\n```",
  "evaluation_criteria": "Code correctness, efficiency, following best practices"
}
```

## Editing Code

### Code Style

- Use 100 character line length (configured in `pyproject.toml`)
- Follow PEP 8 conventions
- Format with Black: `make format`
- Lint with Ruff: `make lint`

### Adding Features

1. Install dev dependencies: `uv sync --all-extras`
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test: `uv run python main.py start`
5. Format and lint: `make format && make lint`
6. Commit and push

### Key Files

- `main.py` - CLI interface
- `questions.py` - Question management and random selection
- `session.py` - Session persistence
- `evaluator.py` - Answer evaluation logic
- `ollama_client.py` - Ollama integration
- `config.py` - Configuration

## Improving Evaluation

The LLM evaluation for open-ended and coding questions happens in:

1. **Prompts**: `config.py` - `EVALUATION_PROMPT_TEMPLATE` and `CODING_EVALUATION_PROMPT`
2. **Parsing**: `ollama_client.py` - `_parse_evaluation()` method
3. **Logic**: `evaluator.py` - `_evaluate_open_ended()` and `_evaluate_coding()`

To improve evaluation:
- Refine prompts in `config.py` for clearer evaluation criteria
- Update parsing logic if LLM response format changes
- Adjust scoring logic in `evaluator.py`

## Extending the App

### Adding a New Feature

1. Write the feature in a new module or extend existing ones
2. Update `main.py` to expose new commands
3. Add tests if applicable
4. Update README.md with usage instructions
5. Update `pyproject.toml` if new dependencies are needed

### Adding Dependencies

```bash
# Add a regular dependency
uv add new-package

# Add a dev dependency
uv add --dev new-dev-package
```

## Running Tests

Currently, there are no automated tests. To add them:

1. Install pytest: `uv add --dev pytest`
2. Create test files: `tests/test_*.py`
3. Run tests: `uv run pytest`

## Reporting Issues

When reporting issues, include:
- Python version (`python --version`)
- uv version (`uv --version`)
- Error message and traceback
- Steps to reproduce
- Expected vs actual behavior

## Questions & Discussion

For questions about contributing:
- Check existing issues
- Read the architecture section in README.md
- Explore the code comments

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for making interview prep better for everyone! 🎉
