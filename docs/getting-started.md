# Getting Started

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)
- Git + GitHub CLI (`gh`)

## Setup

```bash
# Clone
git clone https://github.com/eordaxd/ai-pocs.git
cd ai-pocs

# Set up env vars
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Starting a New Experiment

Experiments are fast, minimal, and disposable.

```bash
./scripts/new-poc.sh experiments <name>
# Example: ./scripts/new-poc.sh experiments claude-streaming
```

This creates `experiments/<name>/` with a ready-to-run `main.py` and `requirements.txt`.

```bash
cd experiments/<name>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Starting a New PoC

PoCs are more structured and meant to be shareable.

```bash
./scripts/new-poc.sh pocs <name>
# Example: ./scripts/new-poc.sh pocs rag-pipeline
```

This creates `pocs/<name>/` with `src/`, `tests/`, and a full README template.

## Promoting a PoC to Its Own Repo

When a PoC is ready to live independently:

```bash
# Create a new repo from the PoC folder
cd pocs/<name>
git init
gh repo create eordaxd/<name> --public --source=. --push
```

## Using Shared Utilities

```python
import sys
sys.path.append("../../shared")  # or set PYTHONPATH

from clients.claude_client import ClaudeClient

client = ClaudeClient()
response = client.message("Hello, Claude!")
print(response)
```
