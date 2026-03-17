import pickle
from pathlib import Path

from .ingestion.loader import load_documents
from .ingestion.chunker import chunk_text
from .retrieval.semantic import SemanticRetriever
from .retrieval.keyword import KeywordRetriever


_CHUNKS_FILE = "chunks.pkl"


class Indexer:
    """Orchestrates document loading, chunking, and index building."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def build(self, docs_dir: Path) -> tuple[SemanticRetriever, KeywordRetriever]:
        """Load documents, chunk them, and build both indices."""
        raw_docs = load_documents(docs_dir)
        if not raw_docs:
            raise ValueError(f"No supported documents found in {docs_dir}")

        all_chunks = []
        for text, metadata in raw_docs:
            all_chunks.extend(chunk_text(text, metadata))

        print(f"  Loaded {len(raw_docs)} document(s) → {len(all_chunks)} chunks")

        # Semantic index
        semantic = SemanticRetriever(str(self.data_dir / "chroma"))
        print("  Building semantic index...")
        semantic.index(all_chunks)

        # Keyword index (in-memory, persisted as pickle)
        keyword = KeywordRetriever()
        keyword.index(all_chunks)

        with open(self.data_dir / _CHUNKS_FILE, "wb") as f:
            pickle.dump(all_chunks, f)

        print("  Done.")
        return semantic, keyword

    def load(self) -> tuple[SemanticRetriever, KeywordRetriever]:
        """Load existing indices from disk."""
        chunks_path = self.data_dir / _CHUNKS_FILE
        if not chunks_path.exists():
            raise FileNotFoundError(
                "Index not found. Run `python src/main.py index` first."
            )

        with open(chunks_path, "rb") as f:
            all_chunks = pickle.load(f)

        semantic = SemanticRetriever(str(self.data_dir / "chroma"))

        keyword = KeywordRetriever()
        keyword.index(all_chunks)

        return semantic, keyword

    def status(self) -> dict:
        """Return index status info."""
        chunks_path = self.data_dir / _CHUNKS_FILE
        if not chunks_path.exists():
            return {"indexed": False}

        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)

        sources = list({c.source for c in chunks})
        return {
            "indexed": True,
            "chunks": len(chunks),
            "sources": sorted(sources),
        }
