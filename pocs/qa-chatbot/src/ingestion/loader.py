from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


def load_documents(docs_dir: Path) -> list[tuple[str, dict]]:
    """
    Load all supported documents from a directory.

    Returns a list of (text, metadata) tuples.
    """
    if not docs_dir.exists():
        raise FileNotFoundError(f"docs directory not found: {docs_dir}")

    results = []
    files = sorted(p for p in docs_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS)

    if not files:
        return []

    for path in files:
        try:
            text = _load_file(path)
            if text.strip():
                results.append((text, {"source": path.name, "path": str(path)}))
        except Exception as e:
            print(f"Warning: could not load {path.name}: {e}")

    return results


def _load_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")

    elif suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(p for p in pages if p.strip())

    elif suffix == ".docx":
        from docx import Document
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    else:
        raise ValueError(f"Unsupported file type: {suffix}")
