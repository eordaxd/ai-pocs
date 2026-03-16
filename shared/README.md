# Shared

Reusable code shared across experiments and PoCs.

## Structure

```
shared/
├── clients/          # API client wrappers
│   └── claude_client.py
└── utils/            # General utilities
    └── __init__.py
```

## Usage

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

from clients.claude_client import ClaudeClient

client = ClaudeClient()
response = client.message("What is RAG?")
print(response)
```
