# Conventions

## Naming

- **Folders**: `kebab-case` (e.g., `rag-pipeline`, `claude-streaming`)
- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/variables**: `snake_case`

## Experiment Numbering (optional)

Prefix with a zero-padded number to keep experiments ordered:

```
experiments/
├── 001-basic-completion/
├── 002-streaming/
├── 003-tool-use/
```

## Commit Messages

Use conventional commits:

```
feat: add RAG pipeline PoC
fix: handle streaming timeout
docs: update getting-started guide
chore: add new experiment template
```

## README Template

Every experiment and PoC must have a `README.md` that answers:
1. **What** — what does this do?
2. **Why** — what hypothesis or problem does it explore?
3. **How to run** — exact commands to reproduce
4. **Results / Findings** — what did you learn?

## Secrets

- Never commit `.env` files or API keys
- Always use `.env.example` as the template
- Load secrets via `python-dotenv` or `os.environ`

## Dependencies

- Pin versions in `requirements.txt` (e.g., `anthropic==0.49.0`)
- Use a virtual environment per project (`.venv/`)
