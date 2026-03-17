from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: str
    metadata: dict = field(default_factory=dict)


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        """Retrieve the top_k most relevant chunks for the given query."""
        ...
