"""Shared utilities for AI PoCs."""
import os
import json
from pathlib import Path


def load_prompt(path: str | Path) -> str:
    """Load a prompt from a .txt or .md file."""
    return Path(path).read_text(encoding="utf-8").strip()


def save_json(data: dict | list, path: str | Path) -> None:
    """Save data as pretty-printed JSON."""
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: str | Path) -> dict | list:
    """Load JSON from a file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if it doesn't exist and return the Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
