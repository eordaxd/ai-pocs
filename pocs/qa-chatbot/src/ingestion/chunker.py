import re
from ..retrieval.base import Chunk


def chunk_text(
    text: str,
    metadata: dict,
    chunk_size: int = 400,
    overlap: int = 80,
) -> list[Chunk]:
    """
    Split text into overlapping chunks of approximately chunk_size characters.
    Splits at sentence boundaries where possible.
    """
    source = metadata.get("source", "unknown")
    sentences = _split_sentences(text)

    chunks: list[Chunk] = []
    current_sentences: list[str] = []
    current_len = 0

    for sentence in sentences:
        s_len = len(sentence)

        if current_len + s_len > chunk_size and current_sentences:
            # Emit current chunk
            chunk_text_str = " ".join(current_sentences)
            chunks.append(Chunk(
                text=chunk_text_str,
                source=source,
                chunk_id=f"{source}_chunk_{len(chunks)}",
                metadata=metadata.copy(),
            ))

            # Keep overlap
            overlap_sentences = _take_overlap(current_sentences, overlap)
            current_sentences = overlap_sentences
            current_len = sum(len(s) for s in current_sentences)

        current_sentences.append(sentence)
        current_len += s_len

    if current_sentences:
        chunk_text_str = " ".join(current_sentences)
        chunks.append(Chunk(
            text=chunk_text_str,
            source=source,
            chunk_id=f"{source}_chunk_{len(chunks)}",
            metadata=metadata.copy(),
        ))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using a simple regex."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]


def _take_overlap(sentences: list[str], max_chars: int) -> list[str]:
    """Return the trailing sentences that fit within max_chars."""
    result = []
    chars = 0
    for sentence in reversed(sentences):
        if chars + len(sentence) > max_chars:
            break
        result.insert(0, sentence)
        chars += len(sentence)
    return result
