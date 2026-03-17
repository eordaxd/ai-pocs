import pytest
from src.retrieval.base import Chunk
from src.retrieval.keyword import KeywordRetriever
from src.retrieval.hybrid import HybridRetriever
from src.ingestion.chunker import chunk_text


# --- Fixtures ---

SAMPLE_CHUNKS = [
    Chunk(text="Python is a high-level programming language.", source="doc1.txt", chunk_id="doc1_0"),
    Chunk(text="Machine learning uses algorithms to learn from data.", source="doc2.txt", chunk_id="doc2_0"),
    Chunk(text="Neural networks are inspired by the human brain.", source="doc2.txt", chunk_id="doc2_1"),
    Chunk(text="Python is widely used in data science and AI.", source="doc1.txt", chunk_id="doc1_1"),
    Chunk(text="The capital of France is Paris.", source="doc3.txt", chunk_id="doc3_0"),
]


# --- Chunker tests ---

def test_chunk_text_basic():
    text = "Hello world. This is a test. It has three sentences."
    chunks = chunk_text(text, {"source": "test.txt"}, chunk_size=100, overlap=20)
    assert len(chunks) >= 1
    assert all(c.source == "test.txt" for c in chunks)
    assert all(c.chunk_id.startswith("test.txt_chunk_") for c in chunks)


def test_chunk_text_overlap():
    # Long enough text to force multiple chunks
    sentences = ["Sentence number {}.".format(i) for i in range(20)]
    text = " ".join(sentences)
    chunks = chunk_text(text, {"source": "long.txt"}, chunk_size=80, overlap=30)
    assert len(chunks) > 1


# --- Keyword retriever tests ---

def test_keyword_retriever_basic():
    retriever = KeywordRetriever()
    retriever.index(SAMPLE_CHUNKS)
    results = retriever.retrieve("Python programming", top_k=2)
    assert len(results) <= 2
    sources = [r.text for r in results]
    assert any("Python" in t for t in sources)


def test_keyword_retriever_no_match():
    retriever = KeywordRetriever()
    retriever.index(SAMPLE_CHUNKS)
    results = retriever.retrieve("quantum physics superconductors", top_k=3)
    # BM25 may return empty if no matching tokens
    assert isinstance(results, list)


def test_keyword_retriever_empty_index():
    retriever = KeywordRetriever()
    retriever.index([])
    results = retriever.retrieve("anything", top_k=5)
    assert results == []


# --- Hybrid retriever tests (with mock semantic) ---

class MockSemanticRetriever:
    """Returns chunks in reverse order to differ from keyword results."""
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        return list(reversed(self.chunks))[:top_k]


def test_hybrid_retriever_combines_results():
    semantic = MockSemanticRetriever(SAMPLE_CHUNKS)
    keyword = KeywordRetriever()
    keyword.index(SAMPLE_CHUNKS)

    hybrid = HybridRetriever(semantic, keyword)
    results = hybrid.retrieve("Python data science", top_k=3)

    assert len(results) <= 3
    assert all(isinstance(r, Chunk) for r in results)


def test_hybrid_rrf_deduplication():
    """Same chunk should appear only once even if in both result lists."""
    semantic = MockSemanticRetriever(SAMPLE_CHUNKS)
    keyword = KeywordRetriever()
    keyword.index(SAMPLE_CHUNKS)

    hybrid = HybridRetriever(semantic, keyword)
    results = hybrid.retrieve("Python", top_k=10)

    chunk_ids = [r.chunk_id for r in results]
    assert len(chunk_ids) == len(set(chunk_ids)), "Duplicate chunks in hybrid results"
