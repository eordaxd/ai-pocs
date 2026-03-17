# Q&A Chatbot

A document Q&A chatbot with multiple retrieval strategies using RAG (Retrieval-Augmented Generation).

## What

Drop documents into `docs/`, index them, then ask questions in a conversational CLI. Supports PDF, TXT, DOCX, and Markdown files.

## Why

Explore and compare different retrieval strategies for RAG:
- **Semantic** — dense vector search via sentence-transformers + ChromaDB
- **Keyword (BM25)** — sparse keyword matching
- **Hybrid** — Reciprocal Rank Fusion combining semantic + keyword
- **Compressed** — semantic retrieval + LLM contextual compression

## How to run

```bash
# 1. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Copy env file and add your key
cp .env.example .env

# 3. Drop documents into docs/
cp /path/to/your/document.pdf docs/

# 4. Index documents
python src/main.py index

# 5. Start chatting (default: hybrid strategy)
python src/main.py chat

# Use a specific strategy
python src/main.py chat --strategy semantic
python src/main.py chat --strategy keyword
python src/main.py chat --strategy hybrid
python src/main.py chat --strategy compressed
```

## Retrieval Strategies

| Strategy | Technique | Best for |
|---|---|---|
| `semantic` | Dense vector search (cosine similarity) | Conceptual / paraphrase queries |
| `keyword` | BM25 sparse retrieval | Exact term matches |
| `hybrid` | Reciprocal Rank Fusion (RRF) | General purpose, most robust |
| `compressed` | Semantic + LLM extraction | Precision, reduces noise |

## Project layout

```
docs/       # Drop your documents here
data/       # Auto-generated index (gitignored)
src/        # Source code
  ingestion/  # Document loading & chunking
  retrieval/  # Retrieval strategies
tests/      # Unit tests
```

## Future improvements

- [ ] Web UI (FastAPI + React or Gradio)
- [ ] Re-ranking with a cross-encoder model
- [ ] Multi-document chat with source attribution
- [ ] Streaming responses
- [ ] Evaluation harness (RAGAS)
- [ ] Support for URLs and web scraping
