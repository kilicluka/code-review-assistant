"""
LLM client abstraction for the Code Review Assistant.

This module provides a protocol for LLM clients and concrete implementations.
To add a new LLM provider, implement the LLMClient protocol.
"""

from enum import Enum
from typing import Literal, Protocol, TypedDict

import anthropic
import openai


class LLMProvider(Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    # Planned (not yet implemented)
    GEMINI = "gemini"

    @classmethod
    def supported(cls) -> list["LLMProvider"]:
        """Return list of currently implemented providers."""
        return [cls.ANTHROPIC, cls.OPENAI]

    @classmethod
    def is_supported(cls, provider: "LLMProvider") -> bool:
        """Check if a provider is currently implemented."""
        return provider in cls.supported()


class ChatMessage(TypedDict):
    """A single message in a chat conversation."""

    role: Literal["user", "assistant"]
    content: str


class LLMClient(Protocol):
    """Protocol defining the interface for LLM clients."""

    def chat(self, system: str, messages: list[ChatMessage]) -> str:
        """
        Send a chat request to the LLM.

        Args:
            system: System prompt to set the assistant's behavior
            messages: List of chat messages

        Returns:
            The assistant's response text
        """
        ...


class _AnthropicClient:
    """Anthropic Claude implementation of LLMClient. Use create_client() instead."""

    def __init__(self, api_key: str, model: str, max_tokens: int):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def chat(self, system: str, messages: list[ChatMessage]) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text


class _OpenAIClient:
    """OpenAI implementation of LLMClient. Use create_client() instead."""

    def __init__(self, api_key: str, model: str, max_tokens: int):
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def chat(self, system: str, messages: list[ChatMessage]) -> str:
        # OpenAI expects system message as part of messages array
        full_messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        full_messages.extend(messages)

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=full_messages,
        )
        return response.choices[0].message.content or ""


def create_client(
    provider: LLMProvider, api_key: str, model: str, max_tokens: int
) -> LLMClient:
    """
    Factory function to create an LLM client for the specified provider.

    Args:
        provider: The LLM provider to use
        api_key: API key for the provider
        model: Model identifier to use
        max_tokens: Maximum tokens for responses

    Returns:
        An LLM client instance

    Raises:
        ValueError: If the provider is not yet implemented
    """
    if provider == LLMProvider.ANTHROPIC:
        return _AnthropicClient(api_key, model, max_tokens)

    if provider == LLMProvider.OPENAI:
        return _OpenAIClient(api_key, model, max_tokens)

    supported = [p.value for p in LLMProvider.supported()]
    raise ValueError(
        f"Provider '{provider.value}' is not yet implemented. "
        f"Currently supported: {', '.join(supported)}"
    )
