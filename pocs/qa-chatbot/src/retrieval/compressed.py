from typing import Any

from .base import BaseRetriever, Chunk

_COMPRESSION_PROMPT = """\
Extract ONLY the sentences or phrases from the passage below that are directly relevant to answering the question.
Preserve the original wording. If nothing in the passage is relevant, respond with exactly: IRRELEVANT

Question: {query}

Passage:
{text}

Relevant extract:"""


class CompressedRetriever(BaseRetriever):
    """
    Retrieves chunks semantically, then uses Claude to extract only the relevant parts.
    Reduces noise at the cost of extra LLM calls.
    """

    def __init__(self, base_retriever: BaseRetriever, llm_client: Any, fetch_multiplier: int = 3):
        """
        Args:
            base_retriever: Any retriever to use as the first-pass retrieval stage.
            llm_client: An object with a .message(prompt: str) -> str method.
            fetch_multiplier: How many extra chunks to fetch before compression.
        """
        self.base = base_retriever
        self.llm = llm_client
        self.fetch_multiplier = fetch_multiplier

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        candidates = self.base.retrieve(query, top_k=top_k * self.fetch_multiplier)
        if not candidates:
            return []

        compressed: list[Chunk] = []
        for chunk in candidates:
            prompt = _COMPRESSION_PROMPT.format(query=query, text=chunk.text)
            extract = self.llm.message(prompt).strip()

            if extract.upper() == "IRRELEVANT":
                continue

            compressed.append(Chunk(
                text=extract,
                source=chunk.source,
                chunk_id=chunk.chunk_id + "_compressed",
                metadata={**chunk.metadata, "compressed": True},
            ))

            if len(compressed) >= top_k:
                break

        return compressed
