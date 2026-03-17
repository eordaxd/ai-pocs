import chromadb
from sentence_transformers import SentenceTransformer

from .base import BaseRetriever, Chunk


COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class SemanticRetriever(BaseRetriever):
    """Dense vector retrieval using sentence-transformers + ChromaDB."""

    def __init__(self, db_path: str):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

    def index(self, chunks: list[Chunk], batch_size: int = 100) -> None:
        """Clear and rebuild the collection from chunks."""
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            embeddings = self.model.encode([c.text for c in batch]).tolist()
            self.collection.add(
                ids=[c.chunk_id for c in batch],
                embeddings=embeddings,
                documents=[c.text for c in batch],
                metadatas=[{**c.metadata, "source": c.source} for c in batch],
            )

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        count = self.collection.count()
        if count == 0:
            return []

        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, count),
        )

        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            chunk_id = results["ids"][0][i]
            chunks.append(Chunk(
                text=doc,
                source=meta.get("source", "unknown"),
                chunk_id=chunk_id,
                metadata=meta,
            ))
        return chunks
