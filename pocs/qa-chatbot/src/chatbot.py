from typing import Any

from .retrieval.base import BaseRetriever, Chunk


_SYSTEM_PROMPT = """\
You are a precise, helpful assistant that answers questions based solely on the provided document context.

Rules:
- Use ONLY the information from the <context> tags to answer.
- If the answer is not in the context, say clearly: "I don't have enough information in the indexed documents to answer that."
- Be concise and accurate. Cite the source document when relevant.
- For follow-up questions, use the conversation history to maintain coherence."""


class QAChatbot:
    """
    Conversational Q&A chatbot backed by a retriever and an LLM.

    Keeps a clean conversation history (without context blobs) and
    injects fresh context for every new question.
    """

    def __init__(self, retriever: BaseRetriever, llm_client: Any, top_k: int = 5):
        """
        Args:
            retriever: Any BaseRetriever implementation.
            llm_client: An object with a .chat(messages, system) -> str method.
            top_k: Number of chunks to retrieve per query.
        """
        self.retriever = retriever
        self.llm = llm_client
        self.top_k = top_k
        self.history: list[dict] = []

    def ask(self, question: str) -> tuple[str, list[str]]:
        """
        Ask a question and return (answer, list_of_sources).
        Context is retrieved fresh for each question; history is kept clean.
        """
        chunks = self.retriever.retrieve(question, top_k=self.top_k)
        context = _format_context(chunks)

        current_message = f"<context>\n{context}\n</context>\n\nQuestion: {question}"

        messages = self.history + [{"role": "user", "content": current_message}]
        answer = self.llm.chat(messages, system=_SYSTEM_PROMPT)

        # Store clean Q&A in history (no context blob)
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})

        sources = list({c.source for c in chunks})
        return answer, sources

    def clear_history(self) -> None:
        self.history = []


def _format_context(chunks: list[Chunk]) -> str:
    if not chunks:
        return "No relevant context found."
    return "\n\n---\n\n".join(
        f"[Source: {c.source}]\n{c.text}" for c in chunks
    )
