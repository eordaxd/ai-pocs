import numpy as np
from rank_bm25 import BM25Okapi

from .base import BaseRetriever, Chunk


class KeywordRetriever(BaseRetriever):
    """Sparse keyword retrieval using BM25."""

    def __init__(self):
        self.chunks: list[Chunk] = []
        self.bm25: BM25Okapi | None = None

    def index(self, chunks: list[Chunk]) -> None:
        self.chunks = list(chunks)
        tokenized = [self._tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(tokenized)

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        if self.bm25 is None or not self.chunks:
            return []

        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in top_indices if scores[i] > 0]

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()
