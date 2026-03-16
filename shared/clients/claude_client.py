"""
Thin wrapper around the Anthropic SDK for quick reuse across experiments.
"""
import os
from typing import Optional
from dotenv import load_dotenv
import anthropic

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 1024


class ClaudeClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )
        self.model = model
        self.max_tokens = max_tokens

    def message(
        self,
        user_message: str,
        system: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Send a single user message and return the text response."""
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": user_message}],
            **kwargs,
        }
        if system:
            params["system"] = system

        response = self.client.messages.create(**params)
        return response.content[0].text

    def stream(self, user_message: str, system: Optional[str] = None, **kwargs):
        """Stream a response, yielding text chunks."""
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": user_message}],
            **kwargs,
        }
        if system:
            params["system"] = system

        with self.client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield text

    def chat(self, messages: list[dict], system: Optional[str] = None, **kwargs) -> str:
        """Send a multi-turn conversation and return the text response."""
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
            **kwargs,
        }
        if system:
            params["system"] = system

        response = self.client.messages.create(**params)
        return response.content[0].text
