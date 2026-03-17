from .base import BaseRetriever, Chunk
from .semantic import SemanticRetriever
from .keyword import KeywordRetriever


class HybridRetriever(BaseRetriever):
    """
    Combines semantic and keyword retrieval using Reciprocal Rank Fusion (RRF).

    RRF score for document d:  sum_r( 1 / (k + rank_r(d)) )
    where k=60 is the standard smoothing constant.
    """

    def __init__(self, semantic: SemanticRetriever, keyword: KeywordRetriever, k: int = 60):
        self.semantic = semantic
        self.keyword = keyword
        self.k = k

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        fetch_k = top_k * 3

        semantic_results = self.semantic.retrieve(query, top_k=fetch_k)
        keyword_results = self.keyword.retrieve(query, top_k=fetch_k)

        scores: dict[str, float] = {}
        all_chunks: dict[str, Chunk] = {}

        for rank, chunk in enumerate(semantic_results):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (self.k + rank + 1)
            all_chunks[chunk.chunk_id] = chunk

        for rank, chunk in enumerate(keyword_results):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (self.k + rank + 1)
            all_chunks[chunk.chunk_id] = chunk

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        return [all_chunks[cid] for cid in sorted_ids[:top_k]]
